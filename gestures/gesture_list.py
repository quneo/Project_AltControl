
class_map={'d_2lbm': 0, 'd_2lbm+': 1, 'd_2lbm-': 2, 'd_attract': 3, 'd_carousel': 4, 'd_fist_2_palm': 5, 'd_fist_down': 6,
            'd_fist_up': 7, 'd_gun_down': 8, 'd_gun_up': 9, 'd_invert_attract': 10, 'd_lbm': 11, 'd_lbm+': 12, 'd_lbm-': 13,
              'd_left_swing': 14, 'd_palm_2_fist': 15, 'd_rbm+': 16, 'd_rbm-': 17, 'd_right_swing': 18, 'd_slider': 19,
                'static_gesture': 20, 's_1fingerup': 21, 's_2fingerup': 22, 's_2finup': 23, 's_call': 24, 's_fist': 25,
                  's_grab': 26, 's_italian': 27, 's_like': 28, 's_ok': 29, 's_openpalm': 30, 's_pinch': 31}
inverse_class_map = {v: k for k, v in class_map.items()}


dynamic_class_map = {'d_2lbm': 0, 'd_2lbm+': 1, 'd_2lbm-': 2, 'd_attract': 3, 'd_carousel': 4, 'd_fist_2_palm': 5, 'd_fist_down': 6,
                      'd_fist_up': 7, 'd_gun_down': 8, 'd_gun_up': 9, 'd_invert_attract': 10, 'd_lbm': 11, 'd_lbm+': 12, 'd_lbm-': 13,
                        'd_left_swing': 14, 'd_palm_2_fist': 15, 'd_rbm+': 16, 'd_rbm-': 17, 'd_right_swing': 18, 'd_slider': 19, 'static_gesture': 20}
inverse_dynamic_class_map = {v: k for k, v in dynamic_class_map.items()}


static_class_map = {'s_1fingerup': 0, 's_2fingerup': 1, 's_2finup': 2, 's_call': 3, 's_fist': 4, 's_grab': 5, 's_italian': 6,
                     's_like': 7, 's_ok': 8, 's_openpalm': 9, 's_pinch': 10}
inverse_static_class_map = {v: k for k, v in static_class_map.items()}

gestures = inverse_class_map



