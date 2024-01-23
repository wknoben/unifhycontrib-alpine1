import numpy as np
import unifhy


class SubSurfaceComponent(unifhy.component.SubSurfaceComponent):
    """The Alpine1 model
    (`Eder et al., 2003`_)
    is a bucket-type rainfall-runoff model.

    Alpine1 is a simply conceptual rainfall-runoff model originally
    developed for use in the Austrian Alps (`Eder et al., 2003`_).
    It contains a simple degree-day-based snow accumulation and melt
    model, coupled to a basic representation of the soil column. The
    soil column is modelled as a simple bucket with evaporation, 
    surface runoff and baseflow processes. The version used here is 
    derived from the MARRMoT database (`Knoben et al., 2019`_).

    .. _`Eder et al., 2003`: https://doi.org/10.1002/hyp.1325
    .. _`Knoben et al., 2019`: https://doi.org/10.5194/gmd-12-2463-2019
    
    :contributors: Wouter Knoben [1]
    :affiliations:
        1. Schulich School of Engineering, University of Calgary, Canada
    :licence: GPL-3.0
    :copyright: 2024
    :codebase: https://github.com/wknoben/unifhycontrib-alpine1
    """

    # component definition below
    _inwards = {
        'canopy_liquid_throughfall_and_snow_melt_flux',
    }
    _outwards = {
        'surface_runoff_flux_delivered_to_rivers',
        'net_groundwater_flux_to_rivers'
    }
    _inputs_info = {
        'potential_water_evapotranspiration_flux': {
            'units': 'kg m-2 s-1',
            'kind': 'dynamic'
        },
    }
    _outputs_info = {
        'actual_water_evapotranspiration_flux': {
            'units': 'kg m-2 s-1',
            'description': 'evaporation from soil moisture store'
        }
    }
    _parameters_info = {
        'theta_smax': {
            'units': 'mm',
            'description': 'maximum storage in soil moisture store'
        },
        'theta_tc': {
            'units': 'd-1',
            'description': 'runoff coefficient'
        }
    }
    _constants_info = {
        ''rho_water': {
            'description': 'volumetric mass density of liquid water',
            'units': 'kg m-3',
            'default_value': 1e3
        }
    }
    _states_info = {
        'soil_store': {
            'units': 'mm'
        }
    }
    _requires_land_sea_mask = False
    _requires_flow_direction = False
    _requires_cell_area = False

    # component implementation of initialise-run-finalise paradigm below
    def initialise(self, input_name, state_name, parameter_name,
                   constant_name, **kwargs):
        if not self.initialised_states:
            soil_store.set_timestep(-1, 0.) # Initializing at zero for soil is as good as anything

    def run(
            # from exchanger
            canopy_liquid_throughfall_and_snow_melt_flux, # [kg m-2 s-1]
            # component inputs
            potential_water_evapotranspiration_flux, # [kg m-2 s-1]
            # component parameters
            theta_smax, theta_tc, # [mm], [d-1]
            # component states
            soil_store, # [mm]
            # component constants
            rho_water, # [kg m-3]
            **kwargs):

        # This implements Equation 42 in the MARRMoT supplement: dSm/dt = Pr + Qn - Ea - Qse - Qss
        # Source: https://gmd.copernicus.org/articles/12/2463/2019/gmd-12-2463-2019-supplement.pdf

        # Conversion constants
        #  not included in _constants_info because these are fixed - maybe there's a unifhy._constants these can go in?
        seconds_per_day = 86400 # [s d-1]
        mm_per_m = 1000 # [mm m-1]
        kelvin_to_celsius = 273.15 # [offset in degrees]

        # Obtain timestep size
        dt = self.timedelta_in_seconds / seconds_per_day # [d] = [s] / [s d-1]

        # Unit conversion
        Pr_plus_Qn = canopy_liquid_throughfall_and_snow_melt_flux / rho_water * mm_per_m * seconds_per_day # [mm d-1] = [kg m-2 s-1] / [kg m-3] * [mm m-1] * [s d-1]
        Ep = potential_water_evapotranspiration_flux / rho_water * mm_per_m * seconds_per_day # [mm d-1] = [kg m-2 s-1] / [kg m-3] * [mm m-1] * [s d-1]

        # Match parameter names to docs for clarity
        Smax = theta_smax
        tc = theta_tc

        # Compute the change in storage
        #  Note: MARRMoT takes this outside the model equations but here it needs to be inside the component
        #  For simplicity, we'll use a straightforward Explicit Euler implementation to avoid the need to use an iterative procedure
        #
        #  dSm/dt = Pr + Qn - Ea - Qse - Qss  >>  Sm[t] = Sm[t-1] + (Pr[t] + Qn[t] - Ea(Sm[t-1] - Qse(S[t-1] - Qss(S[t-1]) * delta_t
        #
        #  Multiple fluxes leave this store, and all are limited by how much storage is available.
        #  We'll calculate the non-limited rate for each flux first, and then scale them by relative
        #  magnitude later if these unlimited rates would drive the store into the negatives.

        # 1. Get storage at t-1
        soil_old = soil_store.get_timestep(-1)

        # 2. Compute the rates as if they were unlimited by available water
        Ea = np.where(soil_old > 0, Ep, 0) # Eq. 44; [mm d-1]
        Qse = np.where(soil_old >= Smax, Pr_plus_Qn, 0) # Eq. 45; [mm d-1]
        Qss = tc * soil_old # Eq. 46; [mm d-1]

        # 3. Convert fluxes into depths over the time interval
        actual_Pr_plus_Qn = Pr_plus_Qn * dt # [mm] = [mm d-1] * [d]
        actual_Ea = Ea * dt # [mm] = [mm d-1] * [d]
        actual_Qse = Qse * dt # [mm] = [mm d-1] * [d]
        actual_Qss = Qss * dt # [mm] = [mm d-1] * [d]

        # 4. Update the store, and account for cases where the fluxes would overdrain the store
        # 4a. Change in storage from fluxes as computed under (2) and (3)
        delta_S1 = actual_Pr_plus_Qn - actual_Ea - actual_Qse - actual_Qss # all in [mm]

        # 4b. Initial estimate of new stores
        soil_store = soil_old + delta_S1 # [mm]

        # 4c. Update flux estimates for cases where soil went negative
        # Note that we included actual_Pr_plus_Qn in estimate delta_S1 (and even with that we overdrain the store)
        #   so we need to take that into account here too
        if any(soil_store < 0):
            # Determine the scaling factors for each drainage flux
            scale_Ea  = actual_Ea  / (actual_Ea + actual_Qse + actual_Qss) # [-] = [mm] / [mm]
            scale_Qse = actual_Qse / (actual_Ea + actual_Qse + actual_Qss) # [-] = [mm] / [mm]
            scale_Qss = actual_Qss / (actual_Ea + actual_Qse + actual_Qss) # [-] = [mm] / [mm]
            
            # Compute the new fluxes where needed
            actual_Ea  = np.where(soil_store < 0, scale_Ea  * (soil_old + actual_Pr_plus_Qn), actual_Ea) # Update only where needed; [mm]
            actual_Qse = np.where(soil_store < 0, scale_Qse * (soil_old + actual_Pr_plus_Qn), actual_Qse) # Update only where needed; [mm]             
            actual_Qss = np.where(soil_store < 0, scale_Qss * (soil_old + actual_Pr_plus_Qn), actual_Qss) # Update only where needed; [mm]

            # Compute the new storage from updated depths
            delta_S2 = actual_Pr_plus_Qn - actual_Ea - actual_Qse - actual_Qss # all in [mm]
            soil_store = soil_old + delta_S2 # [mm]

            # Prevent roundoff errors from dropping us into negative storage values still
            soil_store = np.where(soil_store < 0, 0, soil_store)

        # 5. Map the internal variables onto the declared output variables
        #  We have the fluxes as depths over the time interval, so we need to convert them back into rates per second
        #  by using the length of the time interval in seconds:
        #  [kg m-2 s-1] = [mm] / [mm m-1] * [kg m-3] / [s]
        surface_runoff_flux_delivered_to_rivers = actual_Qse / mm_per_m * rho_water / self.timedelta_in_seconds
        net_groundwater_flux_to_rivers = actual_Qss / mm_per_m * rho_water / self.timedelta_in_seconds
        actual_water_evapotranspiration_flux = actual_Ea / mm_per_m * rho_water / self.timedelta_in_seconds
        
        return (
            # transfers to other components
            {
                'surface_runoff_flux_delivered_to_rivers': surface_runoff_flux_delivered_to_rivers,
                'net_groundwater_flux_to_rivers': net_groundwater_flux_to_rivers
            },
            # intrinsic component outputs
            {
                'actual_water_evapotranspiration_flux': actual_water_evapotranspiration_flux
            }
        )

    def finalise(self, state_name, parameter_name, constant_name, **kwargs):
        pass
