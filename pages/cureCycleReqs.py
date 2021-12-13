# this code needs to correspond with the constraints outlined in
# section 6.1 of 73-011-ATP-(01)-0A-Base_Panel_Cure_Profile
B_A = 120 * 60  # minimum cure time
D_C = 180 * 60  # minimum post cure time
A = 120 * 60  # minimum initial cure time
C = 3800 * 60  # maximum time between cure and post cure
Emin, Emax = 65, 75  # centigrade
Fmin, Fmax = 85, 100  # centigrade


def cure_bounds(T):
    if Emin < T < Emax:
        return True
    else:
        return False


def postcure_bounds(T):
    if Fmin < T < Fmax:
        return True
    else:
        return False
