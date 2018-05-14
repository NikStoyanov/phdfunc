"""Parser functions for different files in the PhD"""

import mmap
import numpy as np
from pandas import read_csv

class PhdParser():
    """Handles the parsing for different file cases.
    Currently supports:
        - parsing abaqus .inp files
        - inserting symmetry equations for cohesive elements
    """

    def __init__(self, infile):
        """Initialize variables

        Args:
            infile: The file to be parsed.
        """
        self.infile = infile

    def main_parser(self, keyword_start, keyword_end, keyword_file_end):
        """Reads a file to locate a keyword.

        Args:
            keyword_start: The start key phrase.
            keyword_end: The end key phrase.
            keyword_file_end: The end of file phrase.

        Outputs:
            line_num_start: The line number where the keyword_start is found.
            line_num_end: The line number where the keyword_end is found.

        Raises:
            IOError: If wrong file path is given.
            ValueError: If the keyword is not found.
        """

        with open(self.infile, 'r+b') as fid:
            try:
                mfile = mmap.mmap(fid.fileno(), 0, access=mmap.ACCESS_READ)
                line_num_start = mfile.find(keyword_start.encode())
                line_num_end = mfile.find(keyword_end.encode())
                file_num_end = mfile.find(keyword_file_end.encode())

                if line_num_start == -1:
                    raise ValueError("The keyword %s has not been found." % keyword_start)
                if line_num_end == -1:
                    raise ValueError("The keyword %s has not been found." % keyword_end)
                if file_num_end == -1:
                    raise ValueError("The keyword %s has not been found." % keyword_file_end)

                line_count = 0

                for line in iter(mfile.readline, ""):
                    line_count += 1
                    line = str(line)
                    if line.find(keyword_start) != -1:
                        line_start = line_count
                    if line.find(keyword_end) != -1:
                        line_end = line_count
                    if line.find(keyword_file_end) != -1:
                        file_end = line_count + 1
                        break
            except:
                raise IOError("The file %s has not been found." % self.infile)

        return line_start, line_end, file_end

    def cohesive_symmetry_parser(self, node_set, end_key, end_file):
        """Reads an input file from Abaqus to recover a cohesive node set

        Args:
            node_set: The name of the node set which hold the cohesive nodes.
            end_key: The key word to end the search.
            end_file: The key for file end.

        Outputs:
            index: The index of the nodes in the cohesive node set.
        """
        line_num_start, line_num_end, line_file_end = self.main_parser(node_set, end_key, end_file)

        # parse the abaqus matrix missing values will be present
        # numpy would not be able to figure it out so use pandas
        return read_csv(self.infile, sep=',', skiprows=line_num_start,
                        skipfooter=line_file_end-line_num_end,
                        header=None)

        """return np.genfromtxt(self.infile, skip_header=line_num_start,
                             skip_footer=line_file_end-line_num_end,
                             delimiter=',')"""


    def cohesive_symmetry_build(self, args, file_append = False):
        """Builds the symmetry condition for the cohesive model.

        Args:
            args: a dictionary holding the name of the cohesive node sets
                 and the symmetry condition.

        Returns:
            symmout: an ndarray of the symmetry equations consisting of
                    *EQUATION
                    number_of_nodes
                    node_number_1, degree of freedom, symmetry_condition
        """
        # extract parameter values
        coh_set_top = args['coh_set_top']
        coh_set_bt = args['coh_set_bt']
        coh_set_ele = args['coh_set_ele']
        coh_ele_end = args['end_step']
        symm_cond_x = args['symm_x']
        symm_cond_y = args['symm_y']
        symm_nodes = args['symm_nodes']

        abq_keyword = '*EQUATION\n' + str(symm_nodes) + '\n'
        txt_symm_cond_x = str(symm_cond_x)
        txt_symm_cond_y = str(symm_cond_y)

        # parse the abaqus input file and obtain the top and bottom sets
        node_set_top = self.cohesive_symmetry_parser(coh_set_top, coh_set_bt, coh_ele_end)
        node_set_bt = self.cohesive_symmetry_parser(coh_set_bt, coh_set_ele, coh_ele_end)

        # flatten and drop any NaN values
        node_set_top = node_set_top.values.flatten()
        node_set_bt = node_set_bt.values.flatten()

        mask = np.isnan(node_set_top)

        node_set_top = node_set_top[~mask]
        node_set_bt = node_set_bt[~mask]

        symmout = []

        # to build the symmetry we need to write the equations
        for top, bot in zip(node_set_top.T, node_set_bt.T):
            # create the x equation
            top_txt_x = str(int(top)) + ', 1, ' + txt_symm_cond_x + ', '
            bt_txt_x = str(int(bot)) + ', 1, ' + txt_symm_cond_x + '\n'
            x_equation = abq_keyword + top_txt_x + bt_txt_x

            # create the y equation
            top_txt_y = str(int(top)) + ', 2, ' + txt_symm_cond_y + ', '
            bt_txt_y = str(int(bot)) + ', 2, -' + txt_symm_cond_y + '\n'
            y_equation = abq_keyword + top_txt_y + bt_txt_y

            symmout.append(x_equation)
            symmout.append(y_equation)

        return symmout

if __name__ == "__main__":
    DICTI = {'coh_set_top':'Coh_Top',
             'coh_set_bt':'Coh_Bt',
             'coh_set_ele':'*USER ELEMENT',
             'end_step':'*End Step',
             'symm_x':1,
             'symm_y':1,
             'symm_nodes':2}

    a = PhdParser('/home/nik/Desktop/Academic/Modelling/Abaqus/2D_PPR_Experiment_Validation/input_data/Cohesive/Cohesive/Job-1.inp')
    symmout = a.cohesive_symmetry_build(DICTI)

    fob = open('/home/nik/Desktop/Academic/Modelling/Abaqus/2D_PPR_Experiment_Validation/input_data/Cohesive/Cohesive/symm.inp', 'w')
    for item in symmout:
        fob.write("%s\n" % item)
    fob.close()
