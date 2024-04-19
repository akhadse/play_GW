import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')
import cv2
import gwsurrogate
from flask import render_template, jsonify


def generate_video_for_varying_param(input_dict):

    ################
    allowed_params_to_vary = ['q','chiAx', 'chiAy', 'chiAz', 'chiBx', 'chiBy', 'chiBz']
    ################
    
    user_input       = input_dict["user_input"]
    surrogate_params = input_dict["surrogate_params"]
    video_params     = input_dict["video_params"]
    figure_params    = input_dict["figure_params"]

    video_width = video_params["video_width"]
    video_height = video_params["video_height"]
    video_fps = video_params["video_fps"]
    video_name = video_params["video_name"]

    figure_width = figure_params["figure_width"]
    figure_height = figure_params["figure_height"]
    figsize       = (figure_width,figure_height)

    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(video_name, fourcc, video_fps, (video_width, video_height))

    # Get user input values
    choose_parameter_to_vary     = user_input["choose_parameter_to_vary"]     # Choose from 'q', 'chiAx', 'chiAy', 'chiAz', 'chiBx', 'chiBy', 'chiBz'
    parameter_start_value        = user_input["parameter_start_value"]
    parameter_end_value          = user_input["parameter_end_value"]
    parameter_steps              = user_input["parameter_steps"] # performs at around 5 steps/second

    l=user_input["l"]
    m=user_input["m"]

    # Surrogate parameters
    sur_name   = surrogate_params["sur_name"]  
    f_low = surrogate_params["f_low"]
    delta_t = surrogate_params["delta_t"]
    
    sur   = gwsurrogate.LoadSurrogate(sur_name)
    times = np.arange(-4299,99,delta_t)

    #
    fixed_params = [i for i in allowed_params_to_vary if i!=choose_parameter_to_vary]

    parameter_to_vary_values = np.linspace(parameter_start_value,parameter_end_value,parameter_steps)


    for i,param_val in enumerate(parameter_to_vary_values):

        user_input[choose_parameter_to_vary] = param_val

        q     = user_input["q"]
        chiA0 = np.array([user_input["chiAx"],user_input["chiAy"],user_input["chiAz"]])
        chiB0 = np.array([user_input["chiBx"],user_input["chiBy"],user_input["chiBz"]])

        t,h,dyn = sur(q, chiA0, chiB0, f_low=f_low, times=times)

        if i==0: 
            h_max_initial_param = np.max(np.abs(h[(l,m)]))
            h0 = h

            y_max = 1.1*h_max_initial_param
            y_min = -y_max

        f, ((a0, a1), (a2, a3), (a4, a5)) = plt.subplots(3, 2, figsize=figsize, gridspec_kw={'width_ratios': [3, 1]})

        #-----------------------------------------------------------------------------------------------------------------------------
        a0.plot(t,np.real(h0[(l,m)]), label='Initial_parameter', color='red', linewidth='0.8')
        a0.plot(t,np.real(h[(l,m)]), label='Current_parameter')
        a0.set_xlim((t[0],t[-1]))
        a0.set_ylim((y_min,y_max))
        a0.set_xlabel("Time")
        a0.set_ylabel(f"Real(h_{l}{m})")
        a0.legend()
        a0.legend(loc='upper left')
        a0.grid(axis='x')
        
        a1.plot(t,np.real(h0[(l,m)]), label='real_initial_parameter', color='red', linewidth='0.8')
        a1.plot(t,np.real(h[(l,m)]), label='real_current_parameter')
        a1.set_xlim((-200,50))
        a1.set_ylim((y_min,y_max))
        a1.set_xlabel("Time")
        a1.grid(axis='x')
        #-----------------------------------------------------------------------------------------------------------------------------

        a2.plot(t,np.imag(h0[(l,m)]), label='imag_initial_parameter', color='red', linewidth='0.8')
        a2.plot(t,np.imag(h[(l,m)]), label='imag_current_parameter')
        a2.set_xlim((t[0],t[-1]))
        a2.set_ylim((y_min,y_max))  
        a2.set_xlabel("Time")
        a2.set_ylabel(f"Imag(h_{l}{m})")
        a2.grid(axis='x')
        
        a3.plot(t,np.imag(h0[(l,m)]), label='imag_initial_parameter', color='red', linewidth='0.8')
        a3.plot(t,np.imag(h[(l,m)]), label='imag_current_parameter')
        a3.set_xlim((-200,50))
        a3.set_ylim((y_min,y_max))
        a3.set_xlabel("Time")
        a3.grid(axis='x')

        #-----------------------------------------------------------------------------------------------------------------------------
        a4.plot(t,np.abs(h0[(l,m)]), label='abs_initial_parameter', color='red', linewidth='0.8')
        a4.plot(t,np.abs(h[(l,m)]), label='abs_current_parameter')
        a4.set_xlim((t[0],t[-1]))
        a4.set_ylim((0.,y_max))   
        a4.set_xlabel("Time")
        a4.set_ylabel(f"Abs(h_{l}{m})")
        a4.grid(axis='x')
        
        a5.plot(t,np.abs(h0[(l,m)]), label='abs_initial_parameter', color='red', linewidth='0.8')
        a5.plot(t,np.abs(h[(l,m)]), label='abs_current_parameter')
        a5.set_xlim((-200,50))
        a5.set_ylim((0.,y_max))
        a5.set_xlabel("Time")
        a5.grid(axis='x')


        plt.suptitle(f"h_{l}{m} for {choose_parameter_to_vary} = {param_val:.2f}", fontsize=26)

        f.tight_layout()
        
        f.savefig('temp.png')

        img = cv2.imread('temp.png')
        video.write(img)
        
        plt.close()

    # Release video writer
    video.release()
    cv2.destroyAllWindows()
    
    return 


#######################################################
import gwsurrogate
import numpy as np

sur   = gwsurrogate.LoadSurrogate("NRSur7dq4")
times = np.arange(-4299,99,1)
f_low = 0
l,m = 2,2
#######################################################

def generate_sur_GW_for_param(input_dict):

    q     = input_dict["q"]
    chiA0 = np.array([input_dict["chiAx"], input_dict["chiAy"], input_dict["chiAz"]])
    chiB0 = np.array([input_dict["chiBx"] , input_dict["chiBy"], input_dict["chiBz"]])

    t,h,dyn = sur(q, chiA0, chiB0, f_low=f_low, times=times)

    h_lm = h[(l,m)]

    x_values = t
    y_values = np.real(h_lm)
    x_values, y_values = x_values.tolist(), y_values.tolist()
    return jsonify({'x_values': x_values, 'y_values': y_values})