""" Pyrhon wrapper for MDI. """

import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

import ctypes

# attempt to import numpy
try:
    import numpy as np
    import numpy.ctypeslib as npct
    use_numpy = True
except ImportError:
    use_numpy = False

# attempt to import mpi4py
try:
    from mpi4py import MPI
    use_mpi4py = True
except ImportError:
    use_mpi4py = False

# get the name of the MDI library
mdi_name_file = open(dir_path + "/mdi_name","r")
mdi_name = mdi_name_file.read()

# load the MDI library
mdi = ctypes.CDLL(dir_path + "/" + mdi_name)

# MDI Variables
MDI_COMMAND_LENGTH = ctypes.c_int.in_dll(mdi, "MDI_COMMAND_LENGTH").value
MDI_NAME_LENGTH = ctypes.c_int.in_dll(mdi, "MDI_NAME_LENGTH").value
MDI_NULL_COMM = ctypes.c_int.in_dll(mdi, "MDI_NULL_COMM").value
MDI_INT = ctypes.c_int.in_dll(mdi, "MDI_INT").value
MDI_DOUBLE = ctypes.c_int.in_dll(mdi, "MDI_DOUBLE").value
MDI_CHAR = ctypes.c_int.in_dll(mdi, "MDI_CHAR").value
MDI_INT_NUMPY = ctypes.c_int.in_dll(mdi, "MDI_INT_NUMPY").value
MDI_DOUBLE_NUMPY = ctypes.c_int.in_dll(mdi, "MDI_DOUBLE_NUMPY").value
MDI_TCP = ctypes.c_int.in_dll(mdi, "MDI_TCP").value
MDI_MPI = ctypes.c_int.in_dll(mdi, "MDI_MPI").value

# Unit conversions
MDI_METER_TO_BOHR = ctypes.c_double.in_dll(mdi, "MDI_METER_TO_BOHR").value
MDI_ANGSTROM_TO_BOHR = ctypes.c_double.in_dll(mdi, "MDI_ANGSTROM_TO_BOHR").value
MDI_SECOND_TO_AUT = ctypes.c_double.in_dll(mdi, "MDI_SECOND_TO_AUT").value
MDI_PICOSECOND_TO_AUT = ctypes.c_double.in_dll(mdi, "MDI_PICOSECOND_TO_AUT").value
MDI_NEWTON_TO_AUF = ctypes.c_double.in_dll(mdi, "MDI_NEWTON_TO_AUF").value
MDI_JOULE_TO_HARTREE = ctypes.c_double.in_dll(mdi, "MDI_JOULE_TO_HARTREE").value
MDI_KJ_TO_HARTREE = ctypes.c_double.in_dll(mdi, "MDI_KJ_TO_HARTREE").value
MDI_KJPERMOL_TO_HARTREE = ctypes.c_double.in_dll(mdi, "MDI_KJPERMOL_TO_HARTREE").value
MDI_KCALPERMOL_TO_HARTREE = ctypes.c_double.in_dll(mdi, "MDI_KCALPERMOL_TO_HARTREE").value
MDI_EV_TO_HARTREE = ctypes.c_double.in_dll(mdi, "MDI_EV_TO_HARTREE").value
MDI_RYDBERG_TO_HARTREE = ctypes.c_double.in_dll(mdi, "MDI_RYDBERG_TO_HARTREE").value
MDI_KELVIN_TO_HARTREE = ctypes.c_double.in_dll(mdi, "MDI_KELVIN_TO_HARTREE").value


intra_code_comm = None


# MDI_Get_MPI_Code_Rank
mdi.MDI_Get_MPI_Code_Rank.argtypes = []
mdi.MDI_Get_MPI_Code_Rank.restype = ctypes.c_int

# MDI_Set_MPI_Intra_Rank
mdi.MDI_Set_MPI_Intra_Rank.argtypes = [ctypes.c_int]
mdi.MDI_Set_MPI_Intra_Rank.restype = None



# MDI_Init
mdi.MDI_Init.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.c_void_p]
mdi.MDI_Init.restype = ctypes.c_int
def MDI_Init(arg1, comm):
    global intra_code_comm

    # append the _language option, so that MDI knows this is a Python code
    arg1 = arg1 + " _language Python"

    # call MDI_Init
    command = arg1.encode('utf-8')
    if comm is None:
        mpi_communicator_ptr = None
        do_mpi_split = False
    else:
        if use_mpi4py:
            mpi_communicator = MPI._addressof(comm)
            #mpi_communicator_ptr = ctypes.c_int(mpi_communicator)
            mpi_communicator_ptr = ctypes.c_void_p(mpi_communicator)
            do_mpi_split = True
        else:
            raise Exception("MDI Error: An MPI communicator was passed to MPI_Init, but mpi4py is not found")

    ret = mdi.MDI_Init(ctypes.c_char_p(command), mpi_communicator_ptr )

    # split the intra-code communicator
    if do_mpi_split:
        mpi_color = mdi.MDI_Get_MPI_Code_Rank()
        intra_code_comm = comm.Split(mpi_color, comm.Get_rank())
        mdi.MDI_Set_MPI_Intra_Rank( intra_code_comm.Get_rank() )
        comm.Barrier()

    return ret

def MDI_Get_Intra_Code_MPI_Comm():
    global intra_code_comm
    return intra_code_comm

# MDI_Accept_Communicator
mdi.MDI_Accept_Communicator.argtypes = []
mdi.MDI_Accept_Communicator.restype = ctypes.c_int
def MDI_Accept_Communicator():
    return mdi.MDI_Accept_Communicator()

# MDI_Send
mdi.MDI_Send.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.c_int, ctypes.c_int, ctypes.c_int]
mdi.MDI_Send.restype = ctypes.c_int
def MDI_Send(arg1, arg2, arg3, arg4):

    if (arg3 == MDI_INT):
        arg_type = ctypes.c_int
        mdi_type = MDI_INT
    elif (arg3 == MDI_DOUBLE):
        arg_type = ctypes.c_double
        mdi_type = MDI_DOUBLE
    elif (arg3 == MDI_CHAR):
        arg_type = ctypes.c_char
        mdi_type = MDI_CHAR
    elif (arg3 == MDI_INT_NUMPY):
        if not use_numpy:
            raise Exception("MDI Error: Attempting to use a Numpy array, but the Numpy package was not found")
        arg_type = ctypes.c_int
        data = arg1.astype(np.int32)
        data = data.ctypes.data_as(ctypes.c_char_p)
        mdi_type = MDI_INT
    elif (arg3 == MDI_DOUBLE_NUMPY):
        if not use_numpy:
            raise Exception("MDI Error: Attempting to use a Numpy array, but the Numpy package was not found")
        arg_type = ctypes.c_double
        data = arg1.astype(np.float64)
        data = data.ctypes.data_as(ctypes.c_char_p)
        mdi_type = MDI_DOUBLE


    if ( arg3 == MDI_INT or arg3 == MDI_DOUBLE or arg3 == MDI_CHAR ):
        arg_size = ctypes.sizeof(arg_type)
        if arg2 == 1:
            data = (ctypes.c_char*(arg2*arg_size))(arg1)
        else:
            data_temp = (arg_type*arg2)(*arg1)
            data = ctypes.cast(data_temp, ctypes.POINTER(ctypes.c_char))

    return mdi.MDI_Send(data, arg2, ctypes.c_int(mdi_type), arg4)

# MDI_Recv
mdi.MDI_Recv.restype = ctypes.c_int
def MDI_Recv(arg2, arg3, arg4):

    if (arg3 == MDI_INT):
        mdi.MDI_Recv.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.c_int, ctypes.c_int, ctypes.c_int]
        arg_type = ctypes.c_int
        mdi_type = MDI_INT
    elif (arg3 == MDI_DOUBLE):
        mdi.MDI_Recv.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.c_int, ctypes.c_int, ctypes.c_int]
        arg_type = ctypes.c_double
        mdi_type = MDI_DOUBLE
    elif (arg3 == MDI_CHAR):
        mdi.MDI_Recv.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.c_int, ctypes.c_int, ctypes.c_int]
        arg_type = ctypes.c_char
        mdi_type = MDI_CHAR
    elif (arg3 == MDI_INT_NUMPY):
        if not use_numpy:
            raise Exception("MDI Error: Attempting to use a Numpy array, but the Numpy package was not found")
        mdi.MDI_Recv.argtypes = [np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'), 
                                 ctypes.c_int, ctypes.c_int, ctypes.c_int]
        arg_type = ctypes.c_int
        mdi_type = MDI_INT
    elif (arg3 == MDI_DOUBLE_NUMPY):
        if not use_numpy:
            raise Exception("MDI Error: Attempting to use a Numpy array, but the Numpy package was not found")
        mdi.MDI_Recv.argtypes = [np.ctypeslib.ndpointer(dtype=np.float64, ndim=1, flags='C_CONTIGUOUS'), 
                                 ctypes.c_int, ctypes.c_int, ctypes.c_int]
        arg_type = ctypes.c_double
        mdi_type = MDI_DOUBLE

    if (arg3 == MDI_DOUBLE_NUMPY):
        arg1 = np.zeros(arg2, dtype='float64')
    elif (arg3 == MDI_INT or arg3 == MDI_DOUBLE or arg3 == MDI_CHAR):
        arg_size = ctypes.sizeof(arg_type)
        arg1 = (ctypes.c_char*(arg2*arg_size))()
    ret = mdi.MDI_Recv(arg1, arg2, ctypes.c_int(mdi_type), arg4)

    if (arg3 == MDI_INT_NUMPY):
        return arg1
    elif (arg3 == MDI_DOUBLE_NUMPY):
        return arg1

    result = ctypes.cast(arg1, ctypes.POINTER(arg_type*arg2)).contents

    if (arg3 == MDI_CHAR):
        # if this is an MDI_CHAR, convert it to a python string
        presult = ctypes.cast(result, ctypes.c_char_p).value
        presult = presult.decode('utf-8')
    else:
        if arg2 == 1:
            presult = result[0]
        else:
            presult = [ result[i] for i in range(arg2) ]

    return presult

# MDI_Send_Command
mdi.MDI_Send_Command.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.c_int]
mdi.MDI_Send_Command.restype = ctypes.c_int
def MDI_Send_Command(arg1, arg2):
    command = arg1.encode('utf-8')
    return mdi.MDI_Send_Command(ctypes.c_char_p(command), arg2)

# MDI_Recv_Command
mdi.MDI_Recv_Command.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.c_int]
mdi.MDI_Recv_Command.restype = ctypes.c_int
def MDI_Recv_Command(arg2): 
    arg_size = ctypes.sizeof(ctypes.c_char)
    arg1 = (ctypes.c_char*(MDI_COMMAND_LENGTH*arg_size))()

    ret = mdi.MDI_Recv_Command(arg1, arg2)

    result = ctypes.cast(arg1, ctypes.POINTER(ctypes.c_char*MDI_COMMAND_LENGTH)).contents
    presult = ctypes.cast(result, ctypes.c_char_p).value
    presult = presult.decode('utf-8')

    return presult

# MDI_Conversion_Factor
mdi.MDI_Conversion_Factor.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_char)]
mdi.MDI_Conversion_Factor.restype = ctypes.c_double
def MDI_Conversion_Factor(arg1, arg2):
    in_unit = arg1.encode('utf-8')
    out_unit = arg2.encode('utf-8')
    return mdi.MDI_Conversion_Factor(ctypes.c_char_p(in_unit), ctypes.c_char_p(out_unit))
