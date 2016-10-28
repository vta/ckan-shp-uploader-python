import sys
import time
import threading


import time
def run_long_time(duration):
	print("going to sleep for {0} seconds".format(duration))
	time.sleep(duration)
	return

def run_long_process(function_name, args):
	t1 = threading.Thread(target=function_name, args=args)
	start_t = time.time()
	t1.start()
	spinner = ['-','\\','|','/','-','\\','|','/']
	spinner_i = 0
	progress = 0
	delta_t = 0
	while t1.is_alive():
		delta_t = (time.time() - start_t)
		sys.stdout.write("running... time elapsed: {0:.1f}s  {1}   \r".format(delta_t, spinner[spinner_i]))
		spinner_i = (spinner_i + 1) % len(spinner)
		time.sleep(0.1)
		delta_t = (time.time() - start_t)
		sys.stdout.flush()
		
	print('Done!                           ')
	print('Finished in {0:.2f} seconds'.format(delta_t))


run_long_process(run_long_time, [3])
