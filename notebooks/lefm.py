import numba as nb
import numpy as np
from scipy import integrate
from scipy.optimize import brentq

# Constants
RHO_ICE = 917  # kg m^-3
RHO_WATER = 1000  # kg m^-3
GRAV_CONST = 9.81  # m s^-2
C1 = np.sqrt(np.pi)
C2 = 2 / np.sqrt(np.pi)

@nb.njit
def g1(d_s_tilde):
    """Calculate g1 function with normalized depth d_s_tilde = a/b"""
    return 0.46 + 3.06 * d_s_tilde + 0.84 * (1 - d_s_tilde)**5 + 0.66 * d_s_tilde**2 * (1 - d_s_tilde)**2

@nb.njit
def g2(d_s_tilde):
    """Calculate g2 function with normalized depth d_s_tilde = a/b"""
    return -3.52 * d_s_tilde**2

@nb.njit
def g3(d_s_tilde):
    """Calculate g3 function with normalized depth d_s_tilde = a/b"""
    return (6.17 - 28.22 * d_s_tilde + 34.54 * d_s_tilde**2 - 14.39 * d_s_tilde**3 - 
            (1 - d_s_tilde)**(3/2) - 5.88 * (1 - d_s_tilde)**5 - 
            2.64 * d_s_tilde**2 * (1 - d_s_tilde)**2)

@nb.njit
def g4(d_s_tilde):
    """Calculate g4 function with normalized depth d_s_tilde = a/b"""
    return (-6.63 + 25.16 * d_s_tilde - 31.04 * d_s_tilde**2 + 14.41 * d_s_tilde**3 + 
            2 * (1 - d_s_tilde)**(3/2) + 5.04 * (1 - d_s_tilde)**5 + 
            1.98 * d_s_tilde**2 * (1 - d_s_tilde)**2)

@nb.njit
def G(z_tilde, d_s_tilde):
    """Calculate G function with normalized values z_tilde = z/a and d_s_tilde = a/b"""
    return (g1(d_s_tilde) + g2(d_s_tilde) * z_tilde + 
            g3(d_s_tilde) * z_tilde**2 + g4(d_s_tilde) * z_tilde**3)

@nb.njit
def F_ds_H(d_s, H):
    """
    Calculate F(d_s/H) according to the equation
    """
    # d_s_H = d_s / H
    
    # # Handle edge cases
    # if d_s_H <= 0 or d_s_H >= 1:
    #     return 0.0
    
    term1 = (2 * H) / (np.pi * d_s)
    term2 = np.tan( (np.pi * d_s) / (2 * H) )
    
    numerator = 0.752 + 2.02 * (d_s/H) + 0.37 * (1 - np.sin( (np.pi * d_s) / (2 * H) ) )**3
    denominator = np.cos( (np.pi * d_s) / (2 * H) )
    
    return np.sqrt(term1 * term2) * (numerator / denominator)

F_ds_H = np.vectorize(F_ds_H)

# We can't use njit here because scipy.integrate.quad is not supported by numba
@nb.njit
def integrand_f(z_tilde, d_s_tilde):
    """Integrand for f(d_s_tilde)"""
    return z_tilde * G(z_tilde, d_s_tilde) * (1 - d_s_tilde)**(-3/2) * (1 - z_tilde**2)**(-1/2)
    
def f_d_s_tilde(d_s_tilde):
    """
    Calculate f(d_s_tilde) using scipy's numerical integration
    """
    
    # if d_s_tilde >= 1.0:
    #     return 0.0
    
    # The integrand has a singularity at z_tilde = 1, so we integrate from 0 to 0.9999
    # to avoid numerical issues
    result, _ = integrate.quad(lambda z: integrand_f(z, d_s_tilde), 0, 0.9999999999)
    return result
    
f_d_s_tilde = np.vectorize(f_d_s_tilde)


@nb.njit
def integrand_g(z_tilde, d_s_tilde, d_w_tilde):
    """Integrand for g(d_s_tilde, d_w_tilde)"""
    return (z_tilde - (1 - d_w_tilde)) * G(z_tilde, d_s_tilde) * (1 - d_s_tilde)**(-3/2) * (1 - z_tilde**2)**(-1/2)

def g_d_s_d_w_tilde(d_s_tilde, d_w_tilde):
    """
    Calculate g(d_s_tilde, d_w_tilde) using scipy's numerical integration
    """
    
    # if d_s_tilde >= 1.0 or d_w_tilde <= 0.0:
    #     return 0.0
    
    # Integration limits
    # lower = max(1 - d_w_tilde, 0)
    lower = 1 - d_w_tilde
    upper = 0.9999999999  # Avoid the singularity at z_tilde = 1
    
    # if lower >= upper:
    #     return 0.0
    
    result, _ = integrate.quad(lambda z_tilde: integrand_g(z_tilde, d_s_tilde, d_w_tilde), lower, upper)
    return result
    
g_d_s_d_w_tilde = np.vectorize(g_d_s_d_w_tilde)


def calculate_K_I(d_s, d_w, R_xx, H):
    """
    Calculate the stress intensity factor K_I
    
    Parameters:
    -----------
    d_s : float or np.ndarray
        Surface fracture depth in meters
    d_w : float or np.ndarray
        Water depth in meters
    R_xx : float or np.ndarray
        Resistive stress in Pascals
    H : float or np.ndarray
        Ice thickness in meters
        
    Returns:
    --------
    K_I : float or np.ndarray
        Stress intensity factor in Pa·m^(1/2)
    """

    # Initialize output array
    K_I = np.zeros_like(d_s, dtype=float)
    
    # Calculate normalized parameters
    d_s_tilde = d_s / H
    d_w_tilde = d_w / d_s

    # Water can't be greater in depth than the crevasse thickness (theoretically)
    d_w_tilde = np.clip(d_w_tilde, 0, 1.0)
    
    # Calculate components
    F_term = F_ds_H(d_s, H)
    f_term = f_d_s_tilde(d_s_tilde)
    g_term = g_d_s_d_w_tilde(d_s_tilde, d_w_tilde)
    
    # Calculate K_I
    term1 = C1 * R_xx * d_s**(1/2) * F_term
    term2 = -C2 * RHO_ICE * GRAV_CONST * d_s**(3/2) * f_term
    term3 = C2 * RHO_WATER * GRAV_CONST * d_s**(3/2) * g_term
    
    K_I = term1 + term2 + term3

    # print(term1, term2, term3)

    return K_I
    
calculate_K_I = np.vectorize(calculate_K_I)


# Bonus functions to calculate the three terms seperately
def calculate_K_1(d_s, R_xx, H):
    F_term = F_ds_H(d_s, H)
    term1 = C1 * R_xx * d_s**(1/2) * F_term
    return term1
    
calculate_K_1 = np.vectorize(calculate_K_1)

def calculate_K_2(d_s, H):
    d_s_tilde = d_s / H
    f_term = f_d_s_tilde(d_s_tilde)
    term2 = -C2 * RHO_ICE * GRAV_CONST * d_s**(3/2) * f_term
    return term2

calculate_K_2 = np.vectorize(calculate_K_2)


def calculate_K_3(d_s, d_w, H):
    d_s_tilde = d_s / H
    d_w_tilde = d_w / d_s
    g_term = g_d_s_d_w_tilde(d_s_tilde, d_w_tilde)
    term3 = C2 * RHO_WATER * GRAV_CONST * d_s**(3/2) * g_term
    return term3

calculate_K_3 = np.vectorize(calculate_K_3)


# Calculate crevasse depth for given values
def find_crevasse_depths(d_w, R_xx, H, K_Ic=0.2e6):
    # Broadcast all inputs to the same shape
    d_w_arr, R_xx_arr, H_arr = np.broadcast_arrays(d_w, R_xx, H)
    result = np.empty_like(H_arr, dtype=float)

    # Iterate over flattened arrays
    for idx in np.ndindex(H_arr.shape):
        dw_i = d_w_arr[idx]
        Rxx_i = R_xx_arr[idx]
        H_i = H_arr[idx]

        # IF ANY OF THE INPUTS ARE NAN, RETURN NAN??

        def objective(d_s):
            return calculate_K_I(d_s, dw_i, Rxx_i, H_i) - K_Ic

        surface = 1.0
        bed = H_i - 1.0
        f_surface = objective(surface)
        f_bed = objective(bed)

        # if (f_lower < 0) and (f_upper < 0):
        if (f_surface <= 0):
            result[idx] = surface
        elif (f_surface > 0) and (f_bed > 0):
            result[idx] = bed
        else:
            result[idx] = brentq(objective, surface, bed)

    return result