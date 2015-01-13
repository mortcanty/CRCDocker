from IPython import parallel
import numpy as np
  
def square(x):
        a = np.array(range(x))
        return np.sum(a)
    
def main():
    c = parallel.Client()
    v = c[:]
    v.execute('import numpy as np')
    result= v.map(square,range(10))
    print result.get()
    
if __name__ == '__main__':
    main()
    
    