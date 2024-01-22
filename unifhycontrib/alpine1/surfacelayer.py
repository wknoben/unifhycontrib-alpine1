import unifhy


class SurfaceLayerComponent(unifhy.component.SurfaceLayerComponent):
    """component description here"""

    # component definition below
    _inwards = {
        'soil_water_stress_for_transpiration',
        'soil_water_stress_for_direct_soil_evaporation',
        'standing_water_area_fraction',
        'total_water_area_fraction'
    }
    _outwards = {
        'canopy_liquid_throughfall_and_snow_melt_flux',
        'transpiration_flux_from_root_uptake',
        'direct_water_evaporation_flux_from_soil',
        'water_evaporation_flux_from_standing_water',
        'water_evaporation_flux_from_open_water',
        'direct_throughfall_flux'
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
            soil_water_stress_for_transpiration,
            soil_water_stress_for_direct_soil_evaporation,
            standing_water_area_fraction, total_water_area_fraction,
            # intrinsic component variables
            input_name, parameter_name, constant_name, state_name,
            **kwargs
    ):
        return (
            # transfers to other components
            {
                'canopy_liquid_throughfall_and_snow_melt_flux': 0,
                'transpiration_flux_from_root_uptake': 0,
                'direct_water_evaporation_flux_from_soil': 0,
                'water_evaporation_flux_from_standing_water': 0,
                'water_evaporation_flux_from_open_water': 0,
                'direct_throughfall_flux': 0
            },
            # intrinsic component outputs
            {
                'output_name': 0
            }
        )

    def finalise(self, state_name, parameter_name, constant_name, **kwargs):
        pass
