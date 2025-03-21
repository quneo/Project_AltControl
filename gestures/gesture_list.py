class_map={'d_2rbm': 0, 'd_attract': 1, 'd_carousel': 2, 'd_fist_2_palm': 3, 'd_fist_down': 4, 'd_fist_up': 5, 'd_gun_down': 6, 'd_gun_up': 7,
            'd_invert_attract': 8, 'd_lbm': 9, 'd_left_swing': 10, 'd_palm_2_fist': 11,
              'd_rbm+': 12, 'd_rbm-': 13, 'd_right_swing': 14, 'd_slider': 15, 's_1fingerup': 16, 's_2finup': 17,
                's_call': 18, 's_fist': 19, 's_grab': 20, 's_italian': 21, 's_like': 22, 's_ok': 23, 's_openpalm': 24, 's_pinch': 25, 'None': 26}

inverse_class_map = {v: k for k, v in class_map.items()}


dynamic_class_map = {'d_2rbm': 0, 'd_attract': 1, 'd_carousel': 2, 'd_fist_2_palm': 3, 'd_fist_down': 4, 'd_fist_up': 5, 'd_gun_down': 6, 'd_gun_up': 7, 'd_invert_attract': 8, 'd_lbm': 9, 'd_left_swing': 10, 'd_palm_2_fist': 11, 'd_rbm+': 12, 'd_rbm-': 13, 'd_right_swing': 14, 'd_slider': 15}
inverse_dynamic_class_map = {v: k for k, v in dynamic_class_map.items()}

static_class_map = {'s_1fingerup': 0, 's_2finup': 1, 's_call': 2, 's_fist': 3, 's_grab': 4, 's_italian': 5, 's_like': 6, 's_ok': 7, 's_openpalm': 8, 's_pinch': 9}
inverse_static_class_map = {v: k for k, v in static_class_map.items()}

gestures = inverse_class_map



