from numpy import sin,cos,pi,linspace,arctan,tan,arctan2,sqrt,log,log10,exp
from numpy import arcsin,arccos
from numpy import sinh,cosh
from erros2 import ne
import numpy as np
    
kb = 1.38064852*10**(-23) #m2 kg s-2 K-1
el = 1.602176634*10**(-19) #C,
hplank = 6.62607015e-34
hbar = hplank/(2*pi)
vluz = 299792458
rbhor = 5.2917721067e-11
meletron = 9.109e-31


def grau2rad(grau):
    return grau*pi/180
def rad2grau(rad):
    return 180*rad/pi

#veluz = vluz = 299792458

def ln(x):
    return log(x)
def lambda2nu(lamb):
    return vluz/lamb
def nm2thz(nm):
    return lambda2nu(nm*10**-9)*10**-12

def nu2lamb(nu):
    return vluz/nu
def thz2nm(thz):
    return nu2lamb(thz*10**12)*10**9

def no2lamb(no):
    return (10**-2)/no
def lamb2e(lamb):
    h = 6.62607004e-34
    return h*vluz/lamb
def freq2lambda(freq):
    return vluz/freq

def wn2wl(wn):
    return (1/wn)*10**(-2)

def wn2nm(wn):
    return wn2wl(wn)*10**9

def nm2wn(nm):
    return (10**7)/nm

def rshift2nm(exitation,shift):
    '''excitation in nm, shit in wavenumber'''
    ex = nm2wn(exitation)
    return wn2nm(ex - shift)


def nm2rshift(exitation,shift):
    '''tudo em nm'''

    return (1/exitation - 1/shift)*10**7


def lorentziana(nu,nu0,deltanu,intensidade,y0 = 0,alfa = 0,offset = 0):

    
    if isinstance(nu0,list) == True or isinstance(nu0,np.ndarray) == True:
        nu = np.atleast_2d(nu)
        nu0 = np.atleast_2d(nu0)
        dic = {}
        #checar todos os parametros. Se forem unicos transformar em lista
        for i in ['deltanu','intensidade','y0','alfa','offset']:
            var = locals()[i]
            if isinstance(var,list) != True and isinstance(var,np.ndarray) != True:
                var = np.atleast_2d(np.repeat(var,nu0.shape[1]))
            else:
                var = np.atleast_2d(var)
            dic[i] = var

        deltanu = dic['deltanu'].T
        intensidade = dic['intensidade'].T
        y0 = dic['y0'].T
        alfa = dic['alfa'].T
        nu0 = nu0.T

    if isinstance(nu,list) == True or isinstance(nu,np.ndarray) == True:
        nu = np.atleast_2d(nu)

    if isinstance(offset,list) == True or isinstance(offset,np.ndarray) == True:
        offset = offset[0]

   # print(nu0,deltanu,intensidade,y0,alfa)
            
    deltanu2 = 2*deltanu/(1+exp(alfa*(nu-nu0)))
    res = y0 + intensidade/(1+(4*(nu-nu0)**2)/(deltanu2**2))
    return offset + res.sum(axis = 0)

def teste_lorentziana():
    
    import matplotlib.pyplot as plt
    plt.switch_backend('TkAgg')
    x = np.linspace(-10,10,10000)
    y = lorentziana(x,nu0 = [-3,0,3],
                    deltanu = 0.2,
                    intensidade = [1,1,-1],
                    y0 = 0,
                    alfa = [-10,0,10])
    fig,ax = plt.subplots()

    ax.plot(x,y)
    fig.show()

def gaussiana(nu,nu0,deltanu,intensidade,y0 = 0,alfa = 0,offset = 0):

    ##def gaussiana(x,u,sigma,intensidade,alfa = 0):
    if isinstance(nu0,list) == True or isinstance(nu0,np.ndarray) == True:
        nu = np.atleast_2d(nu)
        nu0 = np.atleast_2d(nu0)
        dic = {}
        #checar todos os parametros. Se forem unicos transformar em lista
        for i in ['deltanu','intensidade','y0','alfa','offset']:
            var = locals()[i]
            if isinstance(var,list) != True and isinstance(var,np.ndarray) != True:
                var = np.atleast_2d(np.repeat(var,nu0.shape[1]))
            else:
                var = np.atleast_2d(var)
            dic[i] = var

        deltanu = dic['deltanu'].T
        intensidade = dic['intensidade'].T
        y0 = dic['y0'].T
        alfa = dic['alfa'].T
        nu0 = nu0.T

    if isinstance(nu,list) == True or isinstance(nu,np.ndarray) == True:
        nu = np.atleast_2d(nu)

    if isinstance(offset,list) == True or isinstance(offset,np.ndarray) == True:
        offset = offset[0]

   # print(nu0,deltanu,intensidade,y0,alfa)
    res = y0 + intensidade*(exp(-(1/2)*((nu-nu0)/deltanu)**2))
    
    return offset + res.sum(axis = 0)

def gaussiana_normalizada(x,u,sigma):
    return (1/(sigma*(pi)**0.5))*exp(-(1/2)*((x-u)/sigma)**2)

def gaussiana_normalizada_2d(x,y,u,sigma):
    d = sqrt(x**2 + y**2)
    return (1/(sigma*(pi)**0.5))*exp(-(1/2)*((d-u)/sigma)**2)

##def gaussiana(x,u,sigma,intensidade,alfa = 0):
##    return intensidade*(exp(-(1/2)*((x-u)/sigma)**2))
##
def gaussiana_y0(x,u,sigma,intensidade,y0):
    return gaussiana(x,u,sigma,intensidade) + y0

def gaussiana_err(x,u,sigma,intensidade):
    return ne(intensidade)*(exp(ne(-(1/2))*((x-ne(u))/ne(sigma))**2))
    
     

gaussiana_string = r'$y(x) = I_0 e^{-(\frac{x-\mu}{2\sigma})^{2}}$'

def gaussiana_convoluida(x,*args):
    res = 0
    for i in range(0,len(args)-1,3):
        
        u = args[i];sig = args[i+1]; intensidade = args[i+2]
        res += gaussiana(x,u,sig,intensidade)


def cosg(t):
    return cos(grau2rad(t))

def sing(t):
    return sin(grau2rad(t))

def tgg(t):
    return tan(grau2rad(t))

def linear3d(x,y):
    
    return x + y
def asing (x):
    import math
    return math.asin(x)*360/(2*pi)

def acosg (x):
    import math
    return math.acos(x)*360/(2*pi)

def u2freq(lista,unidade,exp = 0):
    return (vluz/unidade)*lista*10**exp

def u2lambda(lista,unidade,exp = 0):
        
    if type(lista) == list or type(lista) == tuple:
        lx = [(unidade/i)*10**(exp) for i in lista]
    else:
        lx = (unidade/lista)*10**(exp)
    return lx

def lambda2u(lista,unidade,exp = 0):
        
    if type(lista) == list or type(lista) == tuple:
        lx = [(unidade*10**(exp)/i) for i in lista]
    else:
        lx = (unidade*10**(exp)/lista)
    return lx

def bragg(fi,d,m = 1,theta_rede = 0):
    if theta_rede == 0:
    	pass
    else:
        d = 2*d*cosg(theta_rede/2)
    return 2*d*cosg(fi)/m

def bragg_snell(fi,d,nef,m = 1,theta_rede = 0):
    if theta_rede != 0:
        d = 2*d*cosg(theta_rede/2)
    return (2*d/m)*(nef**2 - sing(fi)**2)**0.5


#reflexao snell

def rho_s(theta,n2, n1 = 1):
    n = n2/n1
    if sing(theta)**2 <= n**2:
        numerador = cosg(theta) - (n**2 - sing(theta)**2)**0.5
        denominador = cosg(theta) + (n**2 - sing(theta)**2)**0.5
        return (numerador/denominador)**2
    else:
        return 1

def rho_p(theta,n2, n1 = 1):
    n = n2/n1
    if sing(theta)**2 <= n**2:
        numerador = -(n**2)*cosg(theta) + (n**2 - sing(theta)**2)**0.5
        denominador = (n**2)*cosg(theta) + (n**2 - sing(theta)**2)**0.5
        return (numerador/denominador)**2
    else:
        return 1


def skl(V,i0,T):
    return i0*exp(el*V/(kb*T))


def asing2float(x):
    try:
        return '%.2f'%asing(x)
    except:
        return '-'


def rede_difracao2(x,lamb,fendas):
    #print(lamb,fendas)
    N = fendas
    d = (0.001)/fendas
    a = d/4
    delta = 2*pi*a*sin(x)/lamb
    beta = 2*pi*d*sin(x)/lamb
    return ((sin(delta/2)/(delta/2))**2)*((sin(N*beta/2)/sin(beta/2))**2)

def rede_difracao(x,lamb,N,d,a):
    
    delta = 2*pi*a*sin(x)/lamb
    beta = 2*pi*d*sin(x)/lamb
    return ((sin(delta/2)/(delta/2))**2)*((sin(N*beta/2)/sin(beta/2))**2)


def u2lambda_tick(x,unidade):
    if x != 0:
        return '%.0f'%u2lambda(x,unidade,9)
    else:
        return '$\\inf$'


def u2freq_tick(x,unidade):
    if x != 0:
        return '%.2f'%u2freq(x,unidade,-12)
    else:
        return '$\\inf$'

def sqrt_tick(x):
    if x >= 0:
        return '%.0f'%(x**0.5)
    else:
        return '-'


def ticks(x):
    if abs(x) <= 1:
        return '%.2f'%asing(x)
    else:
        return '-'


def dispersao(x,w0,gamma):
    return 1 + (w0**2 - x**2)/((w0**2-x**2)**2 + (gamma*x)**2)

def p1q3(k):
    d0 = 10*k
    d1 = gaussiana(k,3,0.1,1)
    d2 = gaussiana(k,3,0.1,1)
    return sin(d0)**2 + 3*sin(d1)**2 + 5*sin(d2)**2

def fresnel_rs(n1,n2,thetai):
    n = n2/n1
    A = cos(thetai) - sqrt(0j + n**2 - sin(thetai)**2)
    B = cos(thetai) + sqrt(0j + n**2 - sin(thetai)**2)
    return (A/B)

def fresnel_rp(n1,n2,thetai):
    n = n2/n1
    A = -(n**2)*cos(thetai) + sqrt(0j + n**2 - sin(thetai)**2)
    B = (n**2)*cos(thetai) + sqrt(0j + n**2 - sin(thetai)**2)
    return (A/B)


def fresnel_tp(n1,n2,thetai):
    cost_theta2 = np.sqrt(1-((n1/n2)*sin(thetai))**2)
    return 2*n1*cos(thetai)/(n2*cos(thetai) + n1*cost_theta2)

def fresnel_ts(n1,n2,thetai):
    cost_theta2 = np.sqrt(1-((n1/n2)*sin(thetai))**2)
    print(cost_theta2)
    return 2*n1*cos(thetai)/(n1*cos(thetai) + n2*cost_theta2)

def dp(l,n1,n2,theta):
	return (l)/(2*pi*sqrt((n1**2)*sin(grau2rad(theta))**2 - n2**2))

def critical_angle(n1,n2):
    return rad2grau(arcsin(n2/n1))

def fresnel_t2(n1,n2,theta1):
    theta1 = grau2rad(theta1)
    return rad2grau(np.arcsin((n1/n2)*np.sin(theta1)))


#datas
ns2day = lambda x: (x*10**-9)/(60*60*24)
day2ns = lambda x: (x*10**9*3600*24)

def gauss_w(w,dn,a):
    t_fwhm = (2*ln(2)*(np.sqrt(1+a**2)))/(pi*dn)
    t_g = t_fwhm/np.sqrt(2*ln(2))
    phi = np.exp(-1j*(0.5*np.arctan(a) + ((a*t_g**2)/(4*(1+a**2)))*w**2))
    return (t_g*np.sqrt(pi)/((1+a**2)**(1/4)))*np.exp(-((w*t_g)**2/(4*(1+a**2))))*phi

def gauss_t(t,dn,a,w0):
    t_fwhm = (2*ln(2)*(np.sqrt(1+a**2)))/(pi*dn)
    t_g = t_fwhm/np.sqrt(2*ln(2))
    phi = np.exp(1j*(w0*t + a*t**2))
    return np.exp(-(t/t_g)**2)*phi



