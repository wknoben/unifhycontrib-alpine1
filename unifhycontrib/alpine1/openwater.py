import unifhy


class OpenWaterComponent(unifhy.component.OpenWaterComponent):
    """component description here"""

    # component definition below
    _inwards = {
        'water_evaporation_flux_from_open_water',
        'direct_throughfall_flux',
        'surface_runoff_flux_delivered_to_rivers',
        'net_groundwater_flux_to_rivers'
    }
    _outwards = {
        'open_water_area_fraction',
        'open_water_surface_height'
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
    _requires_flow_direction = True
    _requires_cell_area = False

    # component implementation of initialise-run-finalise paradigm below
    def initialise(self, input_name, state_name, parameter_name,
                   constant_name, **kwargs):
        if not self.initialised_states:
            state_name.set_timestep(-1, 0.)

    def run(
            self,
            # transfers from other components
            water_evaporation_flux_from_open_water, direct_throughfall_flux,
            surface_runoff_flux_delivered_to_rivers,
            net_groundwater_flux_to_rivers,
            # intrinsic component variables
            input_name, parameter_name, constant_name, state_name,
            **kwargs
    ):
        return (
            # transfers to other components
            {
                'open_water_area_fraction': 0,
                'open_water_surface_height': 0
            },
            # intrinsic component outputs
            {
                'output_name': 0
            }
        )

    def finalise(self, state_name, parameter_name, constant_name, **kwargs):
        pass
