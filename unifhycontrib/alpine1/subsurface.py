import unifhy


class SubSurfaceComponent(unifhy.component.SubSurfaceComponent):
    """component description here"""

    # component definition below
    _inwards = {
        'canopy_liquid_throughfall_and_snow_melt_flux',
        'transpiration_flux_from_root_uptake',
        'direct_water_evaporation_flux_from_soil',
        'water_evaporation_flux_from_standing_water',
        'open_water_area_fraction',
        'open_water_surface_height'
    }
    _outwards = {
        'soil_water_stress_for_transpiration',
        'soil_water_stress_for_direct_soil_evaporation',
        'standing_water_area_fraction',
        'total_water_area_fraction',
        'surface_runoff_flux_delivered_to_rivers',
        'net_groundwater_flux_to_rivers'
    }
    _inputs_info = {
        'input_name': {
            'kind': 'dynamic',
            'units': '1'
        }
    }
    _outputs_info = {
        'output_name': {
            'units': '1'
        }
    }
    _parameters_info = {
        'parameter_name': {
            'units': '1'
        }
    }
    _constants_info = {
        'constant_name': {
            'units': '1',
            'default_value': 1
        }
    }
    _states_info = {
        'state_name': {
            'units': '1'
        }
    }
    _requires_land_sea_mask = False
    _requires_flow_direction = False
    _requires_cell_area = False

    # component implementation of initialise-run-finalise paradigm below
    def initialise(self, input_name, state_name, parameter_name,
                   constant_name, **kwargs):
        if not self.initialised_states:
            state_name.set_timestep(-1, 0.)

    def run(
            self,
            # transfers from other components
            canopy_liquid_throughfall_and_snow_melt_flux,
            transpiration_flux_from_root_uptake,
            direct_water_evaporation_flux_from_soil,
            water_evaporation_flux_from_standing_water,
            open_water_area_fraction, open_water_surface_height,
            # intrinsic component variables
            input_name, parameter_name, constant_name, state_name,
            **kwargs
    ):
        return (
            # transfers to other components
            {
                'soil_water_stress_for_transpiration': 0,
                'soil_water_stress_for_direct_soil_evaporation': 0,
                'standing_water_area_fraction': 0,
                'total_water_area_fraction': 0,
                'surface_runoff_flux_delivered_to_rivers': 0,
                'net_groundwater_flux_to_rivers': 0
            },
            # intrinsic component outputs
            {
                'output_name': 0
            }
        )

    def finalise(self, state_name, parameter_name, constant_name, **kwargs):
        pass
