import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def main():
    title = raw_input('title: ')
    ya,xa = np.histogram(np.random.randn(1000),bins=50)
    ya[0] = 0    
    plt.plot(xa[0:-1],ya)
    plt.title(title)
    plt.show() 
    
    a = np.random.rand(10,3)
    x = np.array(range(10))
    plt.plot(x,a)
    plt.show()
    
    a = np.array(np.random.rand(200,200))
    plt.imshow(a, cmap='gray')
    plt.show()
    
if __name__ == '__main__':
    main()    