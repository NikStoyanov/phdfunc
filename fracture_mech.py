"""Functions for fracture mechanics in the PhD"""

class MMB():
    """Handles the fracture mech functions for MMB specimens"""
    def __init__(self, args):
        # display data
        MAX_FORCE = 250

        # specimen definitions
        FRAC_TOUGH1 = 1000.0 # N/m in x
        FRAC_TOUGH2 = 1000.0 # N/m in y
        MAT_YOUNGS = 122.0*10**3 # E (N/mm2)
        MAT_POIS = 0.25 # Poissons ratio
        SPEC_THICK = 25.4 # B (mm)
        SPEC_HEIGHT = 1.56 # h (mm)
        SPEC_CRACK = 33.7 # a0 (mm)
        SPEC_LENGTH = 102.0 # L * 2 (mm)
        OFFCENTRE_LENGTH = 60.0 # c (mm)
        FORCE_LENGTH = SPEC_LENGTH / 2 # L (mm)

    def get_linear_beamt_data(self, force_max):
        """Obtain an analytical solution. The deflection is calculated from beam theory
        for the end of the beam and provides an upper bound.
        """

        # opening and force
        spec_defl = []
        spec_force = []

        # calculation steps
        force_step = 5
        step_counter = 0
        spec_total_force = 0

        # calculate parameters
        param_stiffness = calc_stiffness()

        # initialize steps
        spec_force.insert(step_counter, 0)
        spec_defl.insert(step_counter, 0)
        step_counter = step_counter + 1

        # calculate the deflection (mm) for a given force (N)
        while spec_total_force < force_max:
            spec_force.insert(step_counter, spec_force[step_counter - 1] + force_step)

            inc_fac1 = 2 * ((3 * OFFCENTRE_LENGTH) - FORCE_LENGTH) / (12 * FORCE_LENGTH)
            inc_fac2 = (SPEC_CRACK**3) / param_stiffness
            incremental_factor = inc_fac1 * inc_fac2

            spec_defl.insert(step_counter, incremental_factor * spec_force[step_counter])
            spec_total_force = spec_total_force + force_step
            step_counter = step_counter + 1

        return spec_defl, spec_force

    def get_lefm_leq(self, force_max):
        """Obtain analytical solution for a < L """

        # opening and force
        spec_defl = []
        spec_force = []

        # calculation steps
        force_step = 5
        step_counter = 0
        spec_total_force = 0

        # calculate parameters
        param_stiffness = calc_stiffness()

        # initialize steps
        # we need to start from somewhere arbitrary far away
        # since the solution goes asymptotic and the plot does
        # start for 0, 0 like the rest of the curves
        spec_force.insert(step_counter, force_max * 100)
        spec_defl.insert(step_counter, force_max * 100)
        step_counter = step_counter + 1
        fracture_tough1 = FRAC_TOUGH1 / (10**3) # N/mm
        fracture_tough2 = FRAC_TOUGH2 / (10**3) # N/mm

        # calculate the deflection (mm) for a given force (N)
        while spec_total_force < force_max:
            # for the first step ignore the arbitrary entry for the start
            if step_counter == 1:
                spec_force.insert(step_counter, force_step)
            else:
                spec_force.insert(step_counter, spec_force[step_counter - 1] + force_step)

            force_mode1 = calc_force_mode1(spec_force[step_counter])
            force_mode2 = calc_force_mode2(spec_force[step_counter])

            inc_fac1 = 2 * force_mode1 / (3 * param_stiffness)
            inc_fac2 = (8 * SPEC_THICK * param_stiffness)
            inc_fac3 = (8 * (force_mode1 ** 2) / (fracture_tough1))
            inc_fac4 = (3 * (force_mode2 ** 2) / (8 * fracture_tough2))

            spec_defl.insert(step_counter, inc_fac1 * (inc_fac2 / (inc_fac3 + inc_fac4)) ** (1.5))

            spec_total_force = spec_total_force + force_step
            step_counter = step_counter + 1

        return spec_defl, spec_force

    def get_lefm_beq(self, force_max):
        """Obtain analytical solution for a > L. It is necessary to
        first solve a quadratic equation for the crack length and then
        use the positive solution to calculate the deflection."""

        # opening and force
        spec_defl = []
        spec_force = []

        # calculation steps
        force_step = 1
        step_counter = 0
        spec_total_force = 0
        force_increase = 0

        # calculate parameters
        param_stiffness = calc_stiffness()

        # initialize steps
        spec_force.insert(step_counter, 0)
        spec_defl.insert(step_counter, 0)
        step_counter = step_counter + 1
        fracture_tough1 = FRAC_TOUGH1 / (10**3) # N/mm
        fracture_tough2 = FRAC_TOUGH2 / (10**3) # N/mm

        # calculate the deflection (mm) for a given force (N)
        while spec_total_force < force_max:
            spec_force.insert(step_counter, spec_force[step_counter - 1] + force_step + force_increase)

            force_mode1 = calc_force_mode1(spec_force[step_counter])
            force_mode2 = calc_force_mode2(spec_force[step_counter])

            # solve the quadratic equation
            inc_fac1 = (1 / (8 * SPEC_THICK * param_stiffness)) * \
                        ((8 * (force_mode1**2) / fracture_tough1) + \
                        (3 * (force_mode2**2) / (8 * fracture_tough2)) - \
                        ((8 * force_mode1 * force_mode2) / fracture_tough2))

            inc_fac2 = -(1 / (8 * SPEC_THICK * param_stiffness)) * \
                        ((3 * FORCE_LENGTH * (force_mode2**2) / (2 * fracture_tough2)) - \
                        (8 * (force_mode1 * force_mode2 * FORCE_LENGTH) / fracture_tough2))

            inc_fac3 = (3 * (force_mode2**2) * (FORCE_LENGTH**2)) / \
                        (16 * SPEC_THICK * param_stiffness * fracture_tough2) - 1

            # we need to calculate at what force does the discriminant is non-negative
            diff = (inc_fac2**2) - (4 * inc_fac1 * inc_fac3)

            if diff <= 0:
                # complex solutions, we need to increase the force
                del spec_force[step_counter]
                force_increase = force_increase + force_step
            else:
                # solutions - to get a straight line we need the 1st in the 1st
                # iteration and 2nd for subsequent iterations

                crack_growth1 = (-inc_fac2 + math.sqrt(diff)) / (2 * inc_fac1)
                crack_growth2 = (-inc_fac2 - math.sqrt(diff)) / (2 * inc_fac1)

                if step_counter == 1:
                    crack_growth = crack_growth1
                else:
                    crack_growth = crack_growth2

                # calculate deflection from beam theory
                tot_fac1 = 2 * ((3 * OFFCENTRE_LENGTH) - FORCE_LENGTH) / (12 * FORCE_LENGTH)
                tot_fac2 = (crack_growth**3) / param_stiffness
                incremental_factor = tot_fac1 * tot_fac2

                spec_defl.insert(step_counter, incremental_factor * spec_force[step_counter])

                # for graph purposes
                if step_counter == 1:
                    spec_defl[step_counter] = 0

                spec_total_force = spec_total_force + force_step + force_increase
                step_counter = step_counter + 1
                force_increase = 0

        return spec_defl, spec_force

    def calc_force_mode1(self, force):
        """calculates the loads associated with mode I"""
        r   eturn ((3 * OFFCENTRE_LENGTH - FORCE_LENGTH) / (4 * FORCE_LENGTH)) * force

    def calc_force_mode2(self, force):
        """calculates the loads associated with mode II"""
        return ((OFFCENTRE_LENGTH + FORCE_LENGTH) / (FORCE_LENGTH)) * force