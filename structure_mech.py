"""Handles the calculation of structural functions"""

class StructuralMech():
    """Defines structural functions"""

    def calc_sec_mom_rect(self, args):
        """calculates the second moment of area for a rectangular section
        based on thickness and height input data

        Inputs:
            args: dictionary of dimensions
        Outputs:
            param_second_mom: second moment of area of a rectangular section
        """

        spec_thick = args['spec_thick']
        spec_height = args['spec_height']
        param_second_mom = ((spec_thick) * (spec_height ** 3)) / 12
        return param_second_mom

    def calc_stiffness(self, args, mat_youngs):
        """calculates the stiffness of the material for a given second moment of area"""
        return self.calc_sec_mom_rect(args) * mat_youngs
