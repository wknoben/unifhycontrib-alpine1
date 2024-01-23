import numpy as np
import unifhy

class SurfaceLayerComponent(unifhy.component.SurfaceLayerComponent):
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
    _inwards = {} # No inputs from other components needed
    _outwards = {
        'canopy_liquid_throughfall_and_snow_melt_flux'
    }
    _inputs_info = {
        'precipitation_flux': {
            'units': 'kg m-2 s-1',
            'kind': 'dynamic',
            'description': 'incoming precipitation, to be divided into rain and snow' 
        },
        'air_temperature': {
            'units': 'K',
            'kind': 'dynamic'
        }
    }
    _outputs_info = {}
    _parameters_info = {
        'theta_tt': {
            'description': 'threshold temperature below which precipitation is assumed to be snow
            'units': 'C'
        },
        'theta_ddf': {
            'description': 'degree-day factor; rate at which accumulated snow melt 
            'units': 'mm C-1 d-1',
        }
    }
    _constants_info = {
        'rho_water': {
            'description': 'volumetric mass density of liquid water',
            'units': 'kg m-3',
            'default_value': 1e3
        }
    }
    _states_info = {
        'snow_store': {
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
            snow_store.set_timestep(-1, 0.) # Initializing at zero for snow makes sense

    def run(
            self,
            # nothing from exchanger
            # component inputs
            precipitation_flux, air_temperature, # [kg m-2 s-1], [K]
            # component parameters
            theta_tt, theta_ddf, # [C], [mm C-1 d-1]
            # component states
            snow_store, # [mm]
            # component constants
            rho_water, # [kg m-3]
            **kwargs):

        # This implements Equation 39 in the MARRMoT supplement: dSn/dt = Ps - Qn
        # Source: https://gmd.copernicus.org/articles/12/2463/2019/gmd-12-2463-2019-supplement.pdf

        # Conversion constants
        #  not included in _constants_info because these are fixed - maybe there's a unifhy._constants these can go in?
        seconds_per_day = 86400 # [s d-1]
        mm_per_m = 1000 # [mm m-1]
        kelvin_to_celsius = 273.15 # [offset in degrees]

        # Obtain timestep size
        dt = self.timedelta_in_seconds / seconds_per_day # [d] = [s] / [s d-1]

        # Unit conversion
        P = precipitation_flux / rho_water * mm_per_m * seconds_per_day # [mm d-1] = [kg m-2 s-1] / [kg m-3] * [mm m-1] * [s d-1]
        T = air_temperature + kelvin_to_celsius # [C]

        # Match parameter names to docs for clarity
        Tt = theta_tt
        ddf = theta_ddf

        # Divide precipitation into snow and rain (Eq. 40)
        Pr = np.where(T  > Tt, P, 0) # [mm d-1]
        Ps = np.where(T <= Tt, P, 0) # [mm d-1]

        # Determine melt rate (Eq. 41)
        Qn = np.where(T >= Tt, ddf*(T-Tt), 0) # [mm d-1] = [mm C-1 d-1] * ([C]-[C])

        # Compute the change in storage
        #  Note: MARRMoT takes this outside the model equations but here it needs to be inside the component
        #  For simplicity, we'll use a straightforward Explicit Euler implementation to avoid the need to use an iterative procedure
        #
        #  dSn/dt = Ps - Qn  >>  Sn[t] = Sn[t-1] + (Ps[t] - Qn[t]) * delta_t 
        #
        #  In this model, snowfall and snowmelt are mutually exclusive, which makes the following a bit easier: at least
        #  1 (or both) of Ps and Qn are zero.

        # 1. Get storage at t-1
        snow_old = snow_store.get_timestep(-1) # [mm]

        # 2. Ensure we don't melt more snow than we have in the store, while accoutning for time step size
        actual_Qn = np.where(Qn * dt > snow_old, snow_old, Qn * dt) # [mm] = [mm d-1]*[d] > [mm], [mm], [mm d-1]*[d]

        # 3. Account for time step size in Pr and Ps
        actual_Pr = Pr * dt # [mm] = [mm d-1] * [d]
        actual_Ps = Ps * dt # [mm] = [mm d-1] * [d]

        # 4. Update the snow store
        snow_store = snow_old + actual_Ps - actual_Qn # [mm] = [mm] + [mm] - [mm]
        snow_store = np.where(snow_store < 0, 0, snow_store) # We shouldn't need this (haha) but it's here to prevent round-off errors accidentally dropping us into the negatives
        
        # 5. Map the internal variables onto the declared output variables
        #  We have the fluxes as depths over the time interval, so we need to convert them back into rates per second
        #  by using the length of the time interval in seconds:
        #  [kg m-2 s-1] = ([mm] + [mm]) / [mm m-1] * [kg m-3] / [s]
        canopy_liquid_throughfall_and_snow_melt_flux = (actual_Pr + actual_Qn) / mm_per_m * rho_water / self.timedelta_in_seconds
        
        return (
            # transfers to other components
            {
                'canopy_liquid_throughfall_and_snow_melt_flux': canopy_liquid_throughfall_and_snow_melt_flux
            }
        )

    def finalise(self, state_name, parameter_name, constant_name, **kwargs):
        pass
