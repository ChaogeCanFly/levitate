import levitate.arrays
import levitate.hardware
import numpy as np

# Tests created with these air properties
from levitate.materials import Air
Air.c = 343
Air.rho = 1.2

# Tests were mostly written before the layout was transposed,
# so a lot of the "expected" positions etc are transposed in the test hardcoding.


def test_rectangular_grid():
    # positions, normals = levitate.arrays.rectangular_grid(shape=(5, 3), spread=10e-3)
    array = levitate.arrays.RectangularArray(shape=(5, 3), transducer_size=10e-3)
    expected_positions = np.array([
        [-0.02, -0.01, 0.],
        [-0.01, -0.01, 0.],
        [0.   , -0.01, 0.],
        [ 0.01, -0.01, 0.],
        [ 0.02, -0.01, 0.],
        [-0.02,  0.  , 0.],
        [-0.01,  0.  , 0.],
        [ 0.  ,  0.  , 0.],
        [ 0.01,  0.  , 0.],
        [ 0.02,  0.  , 0.],
        [-0.02,  0.01, 0.],
        [-0.01,  0.01, 0.],
        [ 0.  ,  0.01, 0.],
        [ 0.01,  0.01, 0.],
        [ 0.02,  0.01, 0.]]).T
    expected_normals = np.array([
        [0., 0., 1.],
        [0., 0., 1.],
        [0., 0., 1.],
        [0., 0., 1.],
        [0., 0., 1.],
        [0., 0., 1.],
        [0., 0., 1.],
        [0., 0., 1.],
        [0., 0., 1.],
        [0., 0., 1.],
        [0., 0., 1.],
        [0., 0., 1.],
        [0., 0., 1.],
        [0., 0., 1.],
        [0., 0., 1.]]).T
    np.testing.assert_allclose(array.transducer_positions, expected_positions)
    np.testing.assert_allclose(array.transducer_normals, expected_normals)


def test_array_offset():
    array = levitate.arrays.RectangularArray(shape=(4, 2), offset=(0.1, -0.2, 1.4))
    expected_positions = np.array([
        [0.085, -0.205, 1.4],
        [0.095, -0.205, 1.4],
        [0.105, -0.205, 1.4],
        [0.115, -0.205, 1.4],
        [0.085, -0.195, 1.4],
        [0.095, -0.195, 1.4],
        [0.105, -0.195, 1.4],
        [0.115, -0.195, 1.4]]).T
    expected_normals = np.array([
        [0., 0., 1.],
        [0., 0., 1.],
        [0., 0., 1.],
        [0., 0., 1.],
        [0., 0., 1.],
        [0., 0., 1.],
        [0., 0., 1.],
        [0., 0., 1.]]).T
    np.testing.assert_allclose(array.transducer_positions, expected_positions)
    np.testing.assert_allclose(array.transducer_normals, expected_normals)


def test_array_normal():
    array = levitate.arrays.RectangularArray(shape=(4, 2), normal=(2, 3, 4))
    expected_positions = np.array([
        [-1.321925551875e-02, -2.328883278124e-03, +8.356290217967e-03],
        [-4.010697510416e-03, -3.516046265624e-03, +4.642383454426e-03],
        [+5.197860497917e-03, -4.703209253125e-03, +9.284766908853e-04],
        [+1.440641850625e-02, -5.890372240625e-03, -2.785430072656e-03],
        [-1.440641850625e-02, +5.890372240625e-03, +2.785430072656e-03],
        [-5.197860497917e-03, +4.703209253125e-03, -9.284766908853e-04],
        [+4.010697510416e-03, +3.516046265624e-03, -4.642383454426e-03],
        [+1.321925551875e-02, +2.328883278124e-03, -8.356290217967e-03]]).T
    expected_normals = np.array([
        [+3.713906763541e-01, +5.570860145312e-01, +7.427813527082e-01],
        [+3.713906763541e-01, +5.570860145312e-01, +7.427813527082e-01],
        [+3.713906763541e-01, +5.570860145312e-01, +7.427813527082e-01],
        [+3.713906763541e-01, +5.570860145312e-01, +7.427813527082e-01],
        [+3.713906763541e-01, +5.570860145312e-01, +7.427813527082e-01],
        [+3.713906763541e-01, +5.570860145312e-01, +7.427813527082e-01],
        [+3.713906763541e-01, +5.570860145312e-01, +7.427813527082e-01],
        [+3.713906763541e-01, +5.570860145312e-01, +7.427813527082e-01]]).T
    np.testing.assert_allclose(array.transducer_positions, expected_positions)
    np.testing.assert_allclose(array.transducer_normals, expected_normals)


def test_array_rotation():
    array = levitate.arrays.RectangularArray(shape=(4, 2), rotation=1, normal=(-1, 4, -2))
    expected_positions = np.array([
        [-8.747019947780e-03, +4.075784833732e-03, +1.252507964135e-02],
        [-9.564871486238e-04, +2.940455719910e-03, +6.359155014132e-03],
        [+6.834045650533e-03, +1.805126606089e-03, +1.932303869110e-04],
        [+1.462457844969e-02, +6.697974922671e-04, -5.972694240310e-03],
        [-1.462457844969e-02, -6.697974922671e-04, +5.972694240310e-03],
        [-6.834045650533e-03, -1.805126606089e-03, -1.932303869110e-04],
        [+9.564871486238e-04, -2.940455719910e-03, -6.359155014132e-03],
        [+8.747019947780e-03, -4.075784833732e-03, -1.252507964135e-02]]).T
    expected_normals = np.array([
        [-2.182178902360e-01, +8.728715609440e-01, -4.364357804720e-01],
        [-2.182178902360e-01, +8.728715609440e-01, -4.364357804720e-01],
        [-2.182178902360e-01, +8.728715609440e-01, -4.364357804720e-01],
        [-2.182178902360e-01, +8.728715609440e-01, -4.364357804720e-01],
        [-2.182178902360e-01, +8.728715609440e-01, -4.364357804720e-01],
        [-2.182178902360e-01, +8.728715609440e-01, -4.364357804720e-01],
        [-2.182178902360e-01, +8.728715609440e-01, -4.364357804720e-01],
        [-2.182178902360e-01, +8.728715609440e-01, -4.364357804720e-01]]).T
    np.testing.assert_allclose(array.transducer_positions, expected_positions)
    np.testing.assert_allclose(array.transducer_normals, expected_normals)


def test_double_sided_grid():
    # positions, normals = levitate.arrays.double_sided_grid(separation=0.5, shape=(2, 2), spread=5e-3, offset=(0.1, -0.2, 1.4), normal=(0.2, -1.4, 2), rotation=1, grid_generator=levitate.arrays.rectangular_grid)
    array = levitate.arrays.DoublesidedArray(levitate.arrays.RectangularArray, separation=0.5, shape=(2, 2), spread=5e-3, offset=(0.1, -0.2, 1.4), normal=(0.2, -1.4, 2), rotation=1)
    expected_positions = np.array([
        [+0.08024900, -0.05992697, +1.19384001],
        [+0.08304868, -0.05640683, +1.19602413],
        [+0.07612649, -0.05781937, +1.19572758],
        [+0.07892617, -0.05429923, +1.19791170],
        [+0.11727496, -0.34435280, +1.60341176],
        [+0.11880835, -0.34038334, +1.60603704],
        [+0.12201648, -0.34539046, +1.60221125],
        [+0.12354987, -0.34142100, +1.60483653]]).T
    expected_normals = np.array([
        [+0.08164966, -0.57154761, +0.81649658],
        [+0.08164966, -0.57154761, +0.81649658],
        [+0.08164966, -0.57154761, +0.81649658],
        [+0.08164966, -0.57154761, +0.81649658],
        [-0.08164966, +0.57154761, -0.81649658],
        [-0.08164966, +0.57154761, -0.81649658],
        [-0.08164966, +0.57154761, -0.81649658],
        [-0.08164966, +0.57154761, -0.81649658]]).T
    np.testing.assert_allclose(array.transducer_positions, expected_positions)
    np.testing.assert_allclose(array.transducer_normals, expected_normals)
    expected_signature = np.array([0, 0, 0, 0, np.pi, np.pi, np.pi, np.pi])
    np.testing.assert_allclose(array.signature(stype='doublesided'), expected_signature)


def test_Array_basics():
    pos, norm = levitate.hardware.dragonfly_grid
    array = levitate.arrays.TransducerArray(pos, norm)
    array.omega = 200000
    np.testing.assert_allclose(2 * np.pi * array.freq, array.omega)
    array.k = 730
    np.testing.assert_allclose(2 * np.pi / array.k, array.wavelength)
    array.wavelength = 8.5e-3
    np.testing.assert_allclose(Air.c, array.wavelength * array.freq)
    array.freq = 41e3
    np.testing.assert_allclose(array.transducer_model.freq, 41e3)

    from levitate.transducers import PlaneWaveTransducer
    array = levitate.arrays.RectangularArray(shape=(4, 4), transducer_model=PlaneWaveTransducer)
    pos = np.array([7e-3, -3e-3, 70e-3])
    np.testing.assert_allclose(array.focus_phases(pos), np.array([+2.069588782645e+00, -2.511641902621e+00, -1.794667262208e+00, -2.103144086214e+00, +2.763870843565e+00, -1.794667262208e+00, -1.067679552580e+00, -1.380498791671e+00, +2.465230031099e+00, -2.103144086214e+00, -1.380498791671e+00, -1.691434660688e+00, +1.189733359830e+00, +2.863786956082e+00, -2.714709695304e+00, -3.017860322253e+00]))
    np.testing.assert_allclose(array.signature(pos, stype='twin'), np.array([-1.570796326795e+00, -1.570796326795e+00, +1.570796326795e+00, +1.570796326795e+00, -1.570796326795e+00, -1.570796326795e+00, -1.570796326795e+00, +1.570796326795e+00, -1.570796326795e+00, -1.570796326795e+00, -1.570796326795e+00, +1.570796326795e+00, -1.570796326795e+00, -1.570796326795e+00, -1.570796326795e+00, +1.570796326795e+00]))
    np.testing.assert_allclose(array.signature(pos, stype='vortex'), np.array([-2.642245931910e+00, -2.356194490192e+00, -1.735945004210e+00, -9.827937232473e-01, -3.050932766389e+00, -2.976443976175e+00, -2.356194490192e+00, -2.449786631269e-01, +2.792821650006e+00, +2.553590050042e+00, +1.815774989922e+00, +7.853981633974e-01, +2.455863142684e+00, +2.158798930342e+00, +1.681453547969e+00, +1.152571997216e+00]))
    np.testing.assert_allclose(array.signature(pos, stype='bottle'), np.array([+3.141592653590e+00, +3.141592653590e+00, +0.000000000000e+00, +0.000000000000e+00, +3.141592653590e+00, +0.000000000000e+00, +0.000000000000e+00, +0.000000000000e+00, +3.141592653590e+00, +0.000000000000e+00, +0.000000000000e+00, +0.000000000000e+00, +3.141592653590e+00, +3.141592653590e+00, +3.141592653590e+00, +3.141592653590e+00]))
    pos = np.array([0.1, -0.2, 0.3])
    np.testing.assert_allclose(array.focus_phases(pos), np.array([-1.4782875, 0.70451472, 2.70433793, -1.76613547, 1.07535199, -3.05482743, -1.08272084, 0.70451472, -2.79668059, -0.67375749, 1.27038374, 3.03192953, -0.52217161, 1.57048339, -2.79668059, -1.0609514]))
    np.testing.assert_allclose(array.signature(pos, stype='twin'), np.array([-1.57079633, -1.57079633, -1.57079633, -1.57079633, -1.57079633, -1.57079633, -1.57079633, -1.57079633, -1.57079633, -1.57079633, -1.57079633, -1.57079633, -1.57079633, -1.57079633, -1.57079633, -1.57079633]))
    np.testing.assert_allclose(array.signature(stype='vortex'), np.array([-2.35619449, -1.89254688, -1.24904577, -0.78539816, -2.8198421, -2.35619449, -0.78539816, -0.32175055, 2.8198421, 2.35619449, 0.78539816, 0.32175055, 2.35619449, 1.89254688, 1.24904577, 0.78539816]))
    np.testing.assert_allclose(array.signature(stype='bottle'), np.array([3.14159265, 0., 0., 3.14159265, 0., 0., 0., 0., 0., 0., 0., 0., 3.14159265, 0., 0., 3.14159265]))


def test_Array_visualizer():
    array = levitate.arrays.RectangularArray(shape=2)
    v_trace = array.visualize.velocity()
    p_trace = array.visualize.pressure()
    t_trace = array.visualize.transducers()
    pos = np.array([0, 0, 0.05])
    signature = array.signature(angle=np.pi, stype='twin')
    array.phases = array.focus_phases(pos) + signature
    trap_pos = array.visualize.find_trap(pos)
    np.testing.assert_allclose(pos, trap_pos, atol=0.1e-3)
    np.testing.assert_allclose(signature, array.signature(pos))


def test_Array_calculations():
    array = levitate.arrays.RectangularArray(shape=2)
    pos = np.array([0.1, -0.2, 0.3])
    expected_result = np.array([
        [-1.60298320e+01+1.39433272e+00j,  7.60005836e+00+1.43149212e+01j, 1.23972894e+01+9.89785204e+00j,  4.72749101e+00-1.52603890e+01j],
        [-2.75579656e+02-3.30839037e+03j, -2.69691942e+03+1.41912500e+03j, -2.02250900e+03+2.51457673e+03j,  2.82526527e+03+8.86498882e+02j],
        [ 5.11790789e+02+6.14415354e+03j,  5.53578197e+03-2.91294080e+03j, 3.94870805e+03-4.90941170e+03j, -6.09662505e+03-1.91297127e+03j],
        [-7.87370445e+02-9.45254391e+03j, -8.51658764e+03+4.48144738e+03j, -5.77859714e+03+7.18450493e+03j,  8.92189032e+03+2.79947015e+03j],
        [ 6.80382495e+05-8.33698641e+04j, -2.91485806e+05-4.94127262e+05j, -5.27798435e+05-3.91154134e+05j, -1.38372830e+05+5.31781607e+05j],
        [ 2.35305285e+06-2.10377336e+05j, -1.13689503e+06-2.12990534e+06j, -1.95769683e+06-1.55833572e+06j, -7.53077687e+05+2.44212524e+06j],
        [ 5.57294329e+06-4.54866720e+05j, -2.65207242e+06-5.06161450e+06j, -4.17057990e+06-3.36464336e+06j, -1.64672816e+06+5.21935967e+06j],
        [-1.26844169e+06+9.63139996e+04j,  5.40041580e+05+1.04492376e+06j, 9.92856867e+05+8.10438183e+05j,  3.62769003e+05-1.12739219e+06j],
        [ 1.95144875e+06-1.48175384e+05j, -8.30833200e+05-1.60757501e+06j, -1.45296127e+06-1.18600710e+06j, -5.30881467e+05+1.64984223e+06j],
        [-3.62411911e+06+2.75182856e+05j,  1.70539446e+06+3.29975923e+06j, 2.83673391e+06+2.31553766e+06j,  1.14558632e+06-3.56018587e+06j],
        [ 2.86670148e+07+1.39550752e+08j,  8.79550534e+07-6.44855683e+07j, 7.10265677e+07-1.14387829e+08j, -1.01799225e+08-1.57149418e+07j],
        [-9.48653965e+07-9.00596323e+08j, -8.15465047e+08+4.51662413e+08j, -6.08347649e+08+7.86174017e+08j,  9.81016375e+08+2.88086328e+08j],
        [ 2.69225703e+08+3.28515432e+09j,  3.00523878e+09-1.57526192e+09j, 1.95396625e+09-2.42520390e+09j, -3.05538963e+09-9.62345944e+08j],
        [-2.90779477e+07-2.61000235e+08j, -1.91908617e+08+1.10366719e+08j, -1.57582477e+08+2.07891701e+08j,  2.12034769e+08+5.76457627e+07j],
        [ 4.47353042e+07+4.01538824e+08j,  2.95244026e+08-1.69794952e+08j, 2.30608503e+08-3.04231758e+08j, -3.10294784e+08-8.43596528e+07j],
        [ 3.80717090e+07+4.85924318e+08j,  4.02816731e+08-2.09323496e+08j, 3.21279107e+08-3.94767783e+08j, -4.51078135e+08-1.44502368e+08j],
        [ 1.08776311e+08+1.38835519e+09j,  1.27205284e+09-6.61021567e+08j, 9.17940305e+08-1.12790795e+09j, -1.42445727e+09-4.56323268e+08j],
        [ 8.12193376e+07+1.15079185e+09j,  9.57197835e+08-4.88115774e+08j, 6.93574595e+08-8.40914649e+08j, -9.64000841e+08-3.15741830e+08j],
        [-1.50835913e+08-2.13718486e+09j, -1.96477450e+09+1.00192185e+09j, -1.35412183e+09+1.64178574e+09j,  2.08021234e+09+6.81337634e+08j],
        [-4.85644305e+07-7.48335747e+08j, -6.23978731e+08+3.13792174e+08j, -4.77252163e+08+5.71923550e+08j,  6.57524678e+08+2.19514891e+08j]])
    np.testing.assert_allclose(array.pressure_derivs(pos), expected_result)

    pos = np.stack(np.mgrid[-10e-3:10e-3:5j, -10e-3:10e-3:4j, -10e-3:10e-3:2j], 0)
    expected_result = np.array([
        [[ -198.361288714467 +541.993167997253j,  -198.361288714467 +541.993167997253j],
         [ -391.018833455589 +666.066211891658j,  -391.018833455589 +666.066211891658j],
         [ -391.018833455589 +666.066211891658j,  -391.018833455589 +666.066211891658j],
         [ -198.361288714467 +541.993167997253j,  -198.361288714467 +541.993167997253j]],
        [[ -153.407692192815 +470.742095245202j,  -153.407692192815 +470.742095245202j],
         [ -124.220622900455  -57.249003463121j,  -124.220622900455  -57.249003463121j],
         [ -124.220622900455  -57.249003463121j,  -124.220622900455  -57.249003463121j],
         [ -153.407692192815 +470.742095245202j,  -153.407692192815 +470.742095245202j]],
        [[ -615.167270124977+1010.072448325248j,  -615.167270124977+1010.072448325248j],
         [-1045.387166791347 +352.560533608739j, -1045.387166791347 +352.560533608739j],
         [-1045.387166791347 +352.560533608740j, -1045.387166791347 +352.560533608740j],
         [ -615.167270124977+1010.072448325248j,  -615.167270124977+1010.072448325248j]],
        [[ -153.407692192815 +470.742095245202j,  -153.407692192815 +470.742095245202j],
         [ -124.220622900456  -57.249003463121j,  -124.220622900456  -57.249003463121j],
         [ -124.220622900456  -57.249003463121j,  -124.220622900456  -57.249003463121j],
         [ -153.407692192815 +470.742095245202j,  -153.407692192815 +470.742095245202j]],
        [[ -198.361288714467 +541.993167997253j,  -198.361288714467 +541.993167997253j],
         [ -391.018833455589 +666.066211891658j,  -391.018833455589 +666.066211891658j],
         [ -391.018833455589 +666.066211891658j,  -391.018833455589 +666.066211891658j],
         [ -198.361288714467 +541.993167997253j,  -198.361288714467 +541.993167997253j]]])
    np.testing.assert_allclose(array.calculate.pressure(pos), expected_result)
    expected_result = np.array([
        [[[+0.184296305590-0.547720201661j, +0.184296305590-0.547720201661j],
         [+0.317239862443-1.157231889740j, +0.317239862443-1.157231889740j],
         [+0.317239862443-1.157231889740j, +0.317239862443-1.157231889740j],
         [+0.184296305590-0.547720201661j, +0.184296305590-0.547720201661j]],

        [[+0.239527098360+0.472536560259j, +0.239527098360+0.472536560259j],
         [-0.163037576566+0.884155721210j, -0.163037576566+0.884155721210j],
         [-0.163037576566+0.884155721210j, -0.163037576566+0.884155721210j],
         [+0.239527098360+0.472536560259j, +0.239527098360+0.472536560259j]],

        [[+0.000000000000+0.000000000000j, +0.000000000000+0.000000000000j],
         [+0.000000000000+0.000000000000j, +0.000000000000+0.000000000000j],
         [+0.000000000000+0.000000000000j, +0.000000000000+0.000000000000j],
         [+0.000000000000+0.000000000000j, +0.000000000000+0.000000000000j]],

        [[-0.239527098360-0.472536560259j, -0.239527098360-0.472536560259j],
         [+0.163037576566-0.884155721210j, +0.163037576566-0.884155721210j],
         [+0.163037576566-0.884155721210j, +0.163037576566-0.884155721210j],
         [-0.239527098360-0.472536560259j, -0.239527098360-0.472536560259j]],

        [[-0.184296305590+0.547720201661j, -0.184296305590+0.547720201661j],
         [-0.317239862443+1.157231889740j, -0.317239862443+1.157231889740j],
         [-0.317239862443+1.157231889740j, -0.317239862443+1.157231889740j],
         [-0.184296305590+0.547720201661j, -0.184296305590+0.547720201661j]]],


       [[[+0.184296305590-0.547720201661j, +0.184296305590-0.547720201661j],
         [+0.491803763628+0.430026919289j, +0.491803763628+0.430026919289j],
         [-0.491803763628-0.430026919289j, -0.491803763628-0.430026919289j],
         [-0.184296305590+0.547720201661j, -0.184296305590+0.547720201661j]],

        [[+0.168059860248-0.910026919460j, +0.168059860248-0.910026919460j],
         [+0.312147059492+0.475747902878j, +0.312147059492+0.475747902878j],
         [-0.312147059492-0.475747902878j, -0.312147059492-0.475747902878j],
         [-0.168059860248+0.910026919460j, -0.168059860248+0.910026919460j]],

        [[+0.485122744920-1.499986514804j, +0.485122744920-1.499986514804j],
         [+0.590096008886+1.302546198699j, +0.590096008886+1.302546198699j],
         [-0.590096008886-1.302546198699j, -0.590096008886-1.302546198699j],
         [-0.485122744920+1.499986514804j, -0.485122744920+1.499986514804j]],

        [[+0.168059860248-0.910026919460j, +0.168059860248-0.910026919460j],
         [+0.312147059492+0.475747902878j, +0.312147059492+0.475747902878j],
         [-0.312147059492-0.475747902878j, -0.312147059492-0.475747902878j],
         [-0.168059860248+0.910026919460j, -0.168059860248+0.910026919460j]],

        [[+0.184296305590-0.547720201661j, +0.184296305590-0.547720201661j],
         [+0.491803763628+0.430026919289j, +0.491803763628+0.430026919289j],
         [-0.491803763628-0.430026919289j, -0.491803763628-0.430026919289j],
         [-0.184296305590+0.547720201661j, -0.184296305590+0.547720201661j]]],


       [[[+0.640427242493-0.843282820182j, -0.640427242493+0.843282820182j],
         [+0.927169358832-1.034716434672j, -0.927169358832+1.034716434672j],
         [+0.927169358832-1.034716434672j, -0.927169358832+1.034716434672j],
         [+0.640427242493-0.843282820182j, -0.640427242493+0.843282820182j]],

        [[+0.422213249306-0.876509032240j, -0.422213249306+0.876509032240j],
         [+0.269898189359-0.299628707843j, -0.269898189359+0.299628707843j],
         [+0.269898189359-0.299628707843j, -0.269898189359+0.299628707843j],
         [+0.422213249306-0.876509032240j, -0.422213249306+0.876509032240j]],

        [[+1.552689116300-1.434408057223j, -1.552689116300+1.434408057223j],
         [+2.147028351610-0.789685524537j, -2.147028351610+0.789685524537j],
         [+2.147028351610-0.789685524537j, -2.147028351610+0.789685524537j],
         [+1.552689116300-1.434408057223j, -1.552689116300+1.434408057223j]],

        [[+0.422213249306-0.876509032240j, -0.422213249306+0.876509032240j],
         [+0.269898189359-0.299628707843j, -0.269898189359+0.299628707843j],
         [+0.269898189359-0.299628707843j, -0.269898189359+0.299628707843j],
         [+0.422213249306-0.876509032240j, -0.422213249306+0.876509032240j]],

        [[+0.640427242493-0.843282820182j, -0.640427242493+0.843282820182j],
         [+0.927169358832-1.034716434672j, -0.927169358832+1.034716434672j],
         [+0.927169358832-1.034716434672j, -0.927169358832+1.034716434672j],
         [+0.640427242493-0.843282820182j, -0.640427242493+0.843282820182j]]]])

    np.testing.assert_allclose(array.calculate.velocity(pos), expected_result)

    expected_result = np.array([[[[-4.919998980856e-07, -4.919998980856e-07],
         [-1.526801908976e-06, -1.526801908976e-06],
         [-1.526801908976e-06, -1.526801908976e-06],
         [-4.919998980856e-07, -4.919998980856e-07]],

        [[+6.276135947530e-07, +6.276135947530e-07],
         [+2.924037518492e-07, +2.924037518492e-07],
         [+2.924037518492e-07, +2.924037518492e-07],
         [+6.276135947530e-07, +6.276135947530e-07]],

        [[-0.000000000000e+00, -0.000000000000e+00],
         [-0.000000000000e+00, -0.000000000000e+00],
         [-0.000000000000e+00, -0.000000000000e+00],
         [-0.000000000000e+00, -0.000000000000e+00]],

        [[-6.276135947530e-07, -6.276135947530e-07],
         [-2.924037518492e-07, -2.924037518492e-07],
         [-2.924037518492e-07, -2.924037518492e-07],
         [-6.276135947530e-07, -6.276135947530e-07]],

        [[+4.919998980856e-07, +4.919998980856e-07],
         [+1.526801908976e-06, +1.526801908976e-06],
         [+1.526801908976e-06, +1.526801908976e-06],
         [+4.919998980856e-07, +4.919998980856e-07]]],


       [[[-4.919998980856e-07, -4.919998980856e-07],
         [+1.982458800214e-07, +1.982458800214e-07],
         [-1.982458800214e-07, -1.982458800214e-07],
         [+4.919998980856e-07, +4.919998980856e-07]],

        [[-9.139547464708e-07, -9.139547464708e-07],
         [+8.362481642211e-07, +8.362481642211e-07],
         [-8.362481642211e-07, -8.362481642211e-07],
         [+9.139547464708e-07, +9.139547464708e-07]],

        [[-2.868905416976e-06, -2.868905416976e-06],
         [-1.532661246324e-06, -1.532661246324e-06],
         [+1.532661246324e-06, +1.532661246324e-06],
         [+2.868905416976e-06, +2.868905416976e-06]],

        [[-9.139547464708e-07, -9.139547464708e-07],
         [+8.362481642211e-07, +8.362481642211e-07],
         [-8.362481642211e-07, -8.362481642211e-07],
         [+9.139547464708e-07, +9.139547464708e-07]],

        [[-4.919998980856e-07, -4.919998980856e-07],
         [+1.982458800214e-07, +1.982458800214e-07],
         [-1.982458800214e-07, -1.982458800214e-07],
         [+4.919998980856e-07, +4.919998980856e-07]]],


       [[[-6.982685029272e-07, +6.982685029272e-07],
         [-1.050036395976e-06, +1.050036395976e-06],
         [-1.050036395976e-06, +1.050036395976e-06],
         [-6.982685029272e-07, +6.982685029272e-07]],

        [[-2.641459970072e-07, +2.641459970072e-07],
         [+1.596715966485e-07, -1.596715966485e-07],
         [+1.596715966485e-07, -1.596715966485e-07],
         [-2.641459970072e-07, +2.641459970072e-07]],

        [[-3.396583724726e-06, +3.396583724726e-06],
         [-3.020243400354e-06, +3.020243400354e-06],
         [-3.020243400354e-06, +3.020243400354e-06],
         [-3.396583724726e-06, +3.396583724726e-06]],

        [[-2.641459970072e-07, +2.641459970072e-07],
         [+1.596715966485e-07, -1.596715966485e-07],
         [+1.596715966485e-07, -1.596715966485e-07],
         [-2.641459970072e-07, +2.641459970072e-07]],

        [[-6.982685029272e-07, +6.982685029272e-07],
         [-1.050036395976e-06, +1.050036395976e-06],
         [-1.050036395976e-06, +1.050036395976e-06],
         [-6.982685029272e-07, +6.982685029272e-07]]]])

    np.testing.assert_allclose(array.calculate.force(pos), expected_result)

    expected_result = np.array([[[[+1.574975834361e-04, +1.574975834361e-04],
         [+3.612560627012e-04, +3.612560627012e-04],
         [+3.612560627012e-04, +3.612560627012e-04],
         [+1.574975834361e-04, +1.574975834361e-04]],

        [[-9.351525122881e-05, -9.351525122881e-05],
         [+1.283518721955e-04, +1.283518721955e-04],
         [+1.283518721955e-04, +1.283518721955e-04],
         [-9.351525122881e-05, -9.351525122881e-05]],

        [[+2.354743363061e-04, +2.354743363061e-04],
         [+1.512829227001e-04, +1.512829227001e-04],
         [+1.512829227001e-04, +1.512829227001e-04],
         [+2.354743363061e-04, +2.354743363061e-04]],

        [[-9.351525122881e-05, -9.351525122881e-05],
         [+1.283518721955e-04, +1.283518721955e-04],
         [+1.283518721955e-04, +1.283518721955e-04],
         [-9.351525122881e-05, -9.351525122881e-05]],

        [[+1.574975834361e-04, +1.574975834361e-04],
         [+3.612560627012e-04, +3.612560627012e-04],
         [+3.612560627012e-04, +3.612560627012e-04],
         [+1.574975834361e-04, +1.574975834361e-04]]],


       [[[+1.574975834361e-04, +1.574975834361e-04],
         [-3.492094301276e-04, -3.492094301276e-04],
         [-3.492094301276e-04, -3.492094301276e-04],
         [+1.574975834361e-04, +1.574975834361e-04]],

        [[+2.025075650989e-05, +2.025075650989e-05],
         [+1.402573367898e-04, +1.402573367898e-04],
         [+1.402573367898e-04, +1.402573367898e-04],
         [+2.025075650989e-05, +2.025075650989e-05]],

        [[+9.860620669292e-04, +9.860620669292e-04],
         [-1.539637172784e-03, -1.539637172784e-03],
         [-1.539637172784e-03, -1.539637172784e-03],
         [+9.860620669292e-04, +9.860620669292e-04]],

        [[+2.025075650989e-05, +2.025075650989e-05],
         [+1.402573367898e-04, +1.402573367898e-04],
         [+1.402573367898e-04, +1.402573367898e-04],
         [+2.025075650989e-05, +2.025075650989e-05]],

        [[+1.574975834361e-04, +1.574975834361e-04],
         [-3.492094301276e-04, -3.492094301276e-04],
         [-3.492094301276e-04, -3.492094301276e-04],
         [+1.574975834361e-04, +1.574975834361e-04]]],


       [[[-2.014099401515e-04, -2.014099401515e-04],
         [-1.247057497942e-04, -1.247057497942e-04],
         [-1.247057497942e-04, -1.247057497942e-04],
         [-2.014099401515e-04, -2.014099401515e-04]],

        [[+1.307203265001e-05, +1.307203265001e-05],
         [+1.824757531845e-04, +1.824757531845e-04],
         [+1.824757531845e-04, +1.824757531845e-04],
         [+1.307203265001e-05, +1.307203265001e-05]],

        [[-9.371055687814e-04, -9.371055687814e-04],
         [+4.867145903251e-04, +4.867145903251e-04],
         [+4.867145903251e-04, +4.867145903251e-04],
         [-9.371055687814e-04, -9.371055687814e-04]],

        [[+1.307203265001e-05, +1.307203265001e-05],
         [+1.824757531845e-04, +1.824757531845e-04],
         [+1.824757531845e-04, +1.824757531845e-04],
         [+1.307203265001e-05, +1.307203265001e-05]],

        [[-2.014099401515e-04, -2.014099401515e-04],
         [-1.247057497943e-04, -1.247057497943e-04],
         [-1.247057497942e-04, -1.247057497942e-04],
         [-2.014099401515e-04, -2.014099401515e-04]]]])

    np.testing.assert_allclose(array.calculate.stiffness(pos), expected_result)