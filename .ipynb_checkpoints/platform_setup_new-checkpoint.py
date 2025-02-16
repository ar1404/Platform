import numpy as np

class Rack():
    """Representation for a Rack within the flow setup."""
    def __init__(self, array_dimensions, offset_x, offset_y, vial2vial_x, vial2vial_y, groundlevel_height):
        self.array_dimensions=array_dimensions
        self.offset_x=offset_x
        self.offset_y=offset_y
        self.vial2vial_x=vial2vial_x
        self.vial2vial_y=vial2vial_y
        self.groundlevel_height=groundlevel_height    
    
    def get_vial_indices(self, vial_position, array_order, tolerance):
        """get indices of a specific vial in a rack with a certain order of the vials
        :returns: a tuple of (i,j) with i=vial-position along x-axis, and j=vial-position along y-axis
        TODO: verify that input is valid type, array dimensions and validation of the inputted values
        """
        indices=np.where(array_order==vial_position)
        # print(str(f'indices are: {indices}'))
        if len(indices)==2 and len(indices[0])==1:
            
            return indices
        elif len(indices)==2 and len(indices[0])==0 and tolerance.lower()=='no':                #tolerance settings
            #REMOVE THIS STATEMENT!!!
            sys.exit(f'fatal error: zero vials with position number {vial_position}')                        #REMOVE THIS STATEMENT!!!
        else:
            logger.warning(f'warning: multiple vials with position number {vial_position}')
            return indices


class Rackcommands(): 
    """Representation for Commands connected to the Rack of the flow setup."""

    def __init__(self,rack,rack_order,rack_position,rack_position_offset_x,rack_position_offset_y):
        self.rack=rack
        self.rack_order=rack_order
        self.rack_position=rack_position
        self.rack_position_offset_x=rack_position_offset_x
        self.rack_position_offset_y=rack_position_offset_y
        
    def get_xy_command(self, vial_pos: int, tolerance: str = 'no') -> str: #speed 125mm/s, force 100%
        """returns a str object command suitable for the liquid handler gx-241"""
        
        index_y, index_x = self.rack.get_vial_indices(vial_pos, self.rack_order, tolerance)
        
        if len(index_x)==len(index_y):
            command=[]
            for i in range(len(index_x)):
                i_x=index_x[i]
                i_y=index_y[i]
                distance_x=self.rack.offset_x + self.rack.vial2vial_x * i_x + (self.rack_position-1)*self.rack_position_offset_x    
                distance_y=self.rack.offset_y + self.rack.vial2vial_y * i_y + (self.rack_position-1)*self.rack_position_offset_y    
                command.append(str(f'X{distance_x}/{distance_y}'))
            return command
        else:
            logger.error("error: len(index_x) != len(index_y) ")



class Vial():
    """Representation for a Vial within the flow setup."""
    def __init__(self,vial_volume_max,vial_usedvolume_max,vial_height,vial_free_depth):
        self.vial_volume_max=vial_volume_max                #volume in mL
        self.vial_usedvolume_max=vial_usedvolume_max        #volume in mL
        self.vial_height=vial_height                        #height in mm
        self.vial_free_depth=vial_free_depth                #depth in mm
        self.sum_liquid_level = 0