import itertools
from instrument.rack_and_vial import Rackcommands
from instrument.gilson import gsioc_protocol 

class spka():
    """
    Class for performing SPKA experiments.
    Be aware the a specific setup of rack and vials are required.
    """ 
    
    
    def __init__(self, no_sub_A, no_sub_B, no_cat, no_spka_points, spka_conv, t0 = True, order_in_A_B = True, order_in_cat = True):
        self.no_sub_A = no_sub_A
        self.no_sub_B = no_sub_B
        self.no_cat = no_cat
        self.no_spka_points = no_spka_points
        self.spka_conv = spka_conv
        self.t0 = t0
        self.order_in_A_B = order_in_A_B
        self.order_in_cat = order_in_cat
    
    
    def spka_combinations(self):
        """
        Params
        --------
        no_sub_A = number of vials in first column (Substrate A)
        no_sub_B = number of vials in second column (Substrate B)
        no_cat = number of vials in third column (Catalyst)
        no_spka_points = number of spka points per profile
        t0 = whether to include a Substrate A t0 at the start of each profile or not
        order_in_A_B = will add kinetic profile to find orders in Substrates A and B
        order_in_cat = will add kinetic profile to find order in Catalyst

        Returns
        --------
        final_combinations = a list containing vial numbers for a full spka run
        """

        # Create lists for each
        sub_A_list = [1 + 4 * i for i in range(self.no_sub_A)]
        sub_B_list = [2 + 4 * i for i in range(self.no_sub_B)]
        cat_list = [3 + 4 * i for i in range(self.no_cat)]

        # Generate all possible combinations
        all_combinations = list(itertools.product(sub_A_list, sub_B_list, cat_list))

        # Reorder combinations so that all combinations with the same elements
        # in sub_B_array and cat_array are grouped together
        combinations = []

        # Iterate through all unique combinations of sub_B_array and cat_array
        # This will go through all sub_A first, then sub_B, then cat
        for c in cat_list:
            for b in sub_B_list:
                for a in sub_A_list:
                    combinations.append((a, b, c))

        # Multiply each combination by no_spka_points to create correct number of entries
        # Take into account if we are including a t0 before each profile or not
        spka_combinations = []
        for combination in combinations:
            if self.t0:
                spka_combinations.append((combination[0],))
            spka_combinations.extend([combination] * self.no_spka_points)
            
        ######## TO DO ########
        # This is where to add a solvent vial - it may have to be in rack 2?
        
        # Each sequence of vials is the same for each experiment (standard, order in A B, order in Cat)
        # Set up the logic for how many repeats
        repeats = 1
        if self.order_in_A_B and self.order_in_cat:
            repeats = 3
        elif self.order_in_A_B or self.order_in_cat:
            repeats = 2
        
        # Repeat the combinations accordingly
        final_combinations = []
        group_size = self.no_spka_points + 1 if self.t0 else self.no_spka_points
        for i in range(0, len(spka_combinations), group_size):
            group = spka_combinations[i:i + group_size]
            for _ in range(repeats):
                final_combinations.extend(group)
        
        return final_combinations
        
        
        
    def spka_volumes(self, vol_sub_A, vol_sub_B, vol_cat, A0, B0_stand, B0_DE, C0_Stand, C0_DE):
        """
        Params
        --------
        vol_sub_A = Maximum volume (mL) of Substrate A stock withdrawn
        vol_sub_B = Maximum volume (mL) of Substrate B stock withdrawn
        vol_cat = Maximum volume (mL) of Catalyst stock withdrawn
        spka_conv = SPKA interval size (i.e., 10%, 20% steps increasing from 0%)
        A0 = Initial concentration of Substrate A across all experiments
        B0_stand = Initial concentration of Substrate B for standard experiment
        B0_DE = Initial concentration of Substrate B for Different Excess experiment
        C0_Stand = Initial concentration of Catalyst for standard experiment
        C0_DE = Initial concentration of Catalyst for Different Excess experiment
        t0 = include a Substrate A t0 at the start of each profile or not
        order_in_A_B = will add kinetic profile to find orders in Substrates A and B
        order_in_cat = will add kinetic profile to find order in Catalyst

        Returns
        --------
        spka_volumes = A list of volumes (mL) to take from each vial for a full SPKA run, an identical partner to that created by spka_combinations
        volume_dict = A dictionary determining the volume (mL) that has been taken from each vial
        """

        # Call above function to get a list containing vial numbers for a full spka run
        final_spka_combination = self.spka_combinations()
        
        # SPKA volume difference currently calculated on % difference between stated initial concentrations for DE experiments
        # Calculate the percentage differences for B and C
        perc_diff_B = (B0_stand - B0_DE) / B0_stand
        perc_diff_C = (C0_Stand - C0_DE) / C0_Stand
        
        # Initialize the list of volumes and volume dictionary
        spka_volumes = []
        combined_volumes = []
        volume_dict = {vial: 0 for combination in final_spka_combination for vial in combination}
        
        # Define a helper function to calculate volumes for each individual kinetic profile
        def calculate_volumes(vol_A, vol_B, vol_C,):
            profile_volumes = []

            # Take into account if we have a t0 at the start of each profile or not
            if self.t0:
                profile_volumes.append((round(vol_A, 2),))
                start = 1
                total_points = self.no_spka_points + 1
            else:
                start = 0
                total_points = self.no_spka_points
            
            for i in range(start, total_points):
                factor = 1 - ((i - start) * self.spka_conv / 100)
                profile_volumes.append((round(vol_A * factor, 3), round(vol_B * factor, 3), round(vol_C * factor, 3)))
            
            return profile_volumes
        
        # Standard experiment
        standard_profile = calculate_volumes(vol_sub_A, vol_sub_B, vol_cat)
        
        # Different Excess in A and B experiment, only if order_in_A_B is True
        if self.order_in_A_B:
            sub_B_DE_profile = calculate_volumes(vol_sub_A, vol_sub_B * (1 - perc_diff_B), vol_cat)
        else:
            sub_B_DE_profile = []
        
        # Different Excess in Catalyst experiment, only if order_in_cat is True
        if self.order_in_cat:
            cat_DE_profile = calculate_volumes(vol_sub_A, vol_sub_B, vol_cat * (1 - perc_diff_C))
        else:
            cat_DE_profile = []
        
        # Combine all profiles into spka_volumes list
        combined_volumes.extend(standard_profile)
        if self.order_in_A_B:
            combined_volumes.extend(sub_B_DE_profile)
        if self.order_in_cat:
            combined_volumes.extend(cat_DE_profile)
        
        # Duplicate the combined volumes no_sub_A * no_sub_B * no_cat times - this accounts for multiple subsrates and catalysts
        spka_volumes = combined_volumes * (self.no_sub_A * self.no_sub_B * self.no_cat)
        
        # Update volume_dict with total volumes taken
        index = 0
        for profile in spka_volumes:
            if len(profile) == 1:
                vial = final_spka_combination[index % len(final_spka_combination)][0]
                volume_dict[vial] += profile[0]
            else:
                for j, vial in enumerate(final_spka_combination[index % len(final_spka_combination)]):
                    volume_dict[vial] += profile[j]
            index += 1
        
        # Round the total volumes in volume_dict to 3 decimal places
        for key in volume_dict:
            volume_dict[key] = round(volume_dict[key], 3)
        
        return spka_volumes, volume_dict
    


    #def spka_time(self):
    ######## TO DO ########
    #"""
    #Calculates the time an SPKA run would take
    #"""
     
    
    def spka_standard(gx241_gsioc_object, dim_gsioc_object, spka_combinations):
        # TO DO: Add volume changes based on spka_conversion!!
            
        # Iterate over each tuple in the list (each separate kinetic profile)
        for tuple in spka_combinations:
            
            # Iterate over each number in the tuple (each reagent in an experiment)
            for element in tuple:
                
                # Find the xy position of the vial        
                vial_xy_pos = rack1_commands.get_xy_command(element)
                
                ##### TO DO #####
                
                # Display vial number - must be a two digit integer
                gx241_gsioc_object.bCommand(f"W{element:02}")
                
                # Go to Vial
                gx241_gsioc_object.bCommand(vial_xy_pos[0])

                # Needle Down - define this distance somewhere above!
                gx241_gsioc_object.bCommand('Z85')

                # Run the pump
                # This will be a while away...
                # How to make the autosampler idle while this is happening?

                # Needle Up
                gx241_gsioc_object.bCommand('Z120')

                # Log the vial and the amount taken
                # Add a logger...
                print(vial_xy_pos)

                # Create air gap
                # Create a tiny airgap with the pump, will this be necessary?
                
            # Go to the DIM and inject
            # Blank the display
            gx241_gsioc_object.bCommand('WBB')
            
            # For now, let's just go to Home instead of the DIM
            gx241_gsioc_object.bCommand('H')
        