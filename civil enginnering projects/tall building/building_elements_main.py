from modules.building_elements import stairs
#stairs
story_height = 3.06 # m
vertical_step = 18 # cm
horizontal_step = 25
(statement,story_height,stairs_height,vertical_step,n_stairs,
horizontal_step,stairs_length,slope_angle,slope_angle_deg)=\
stairs(story_height, vertical_step, horizontal_step)
 # export results
with open("results.txt", "w") as f:
    f.write(f"statement: {statement} \n")
    f.write(f"Story height: {story_height} m\n")
    f.write(f"Stairs height: {stairs_height} cm\n")
    f.write(f"Vertical step: {vertical_step} cm\n")
    f.write(f"Number of stairs: {n_stairs}\n")
    f.write(f"Horizontal step: {horizontal_step} cm\n")
    f.write(f"Stairs length: {stairs_length} cm\n")
    f.write(f"Slope angle (rad): {slope_angle}\n") 
    f.write(f"Slope angle (deg): {slope_angle_deg}\n") 
