import hcsr04, time, piconzero as pz

pz.init()

try:
    while True:
        pz.setOutput(0, 1) # 5% - very dim
        pz.setOutput(1, 1) # 5% - very dim    
        pz.setOutput(2, 1) # 5% - very dim    
        pz.setOutput(3, 1) # 5% - very dim    
        pz.setOutput(4, 1) # 5% - very dim    
        pz.setOutput(5, 1)
        
        time.sleep(1)
        pz.setOutput(0, 0) # 5% - very dim
        pz.setOutput(1, 0) # 5% - very dim    
        pz.setOutput(2, 0) # 5% - very dim    
        pz.setOutput(3, 0) # 5% - very dim    
        pz.setOutput(4, 0) # 5% - very dim    
        pz.setOutput(5, 10)
        time.sleep(1)

except KeyboardInterrupt:
    print

finally:
        #run_event.clear()
        #t.join()
    pz.cleanup()