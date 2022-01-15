from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from PIL import Image,ImageEnhance
import numpy as np
import matplotlib.pyplot as plt
from kivy.core.window import Window
from time import time


def num2e(num):

    if num == '':
        return ''
    if num == None:
        return ''

    if num == 0:
        return '0'
    if num == np.inf:
        return 'inf'

    if type(num) == str:
        num = eval(num)
    if abs(num) > 1:
        n = num
        e = 0
        while abs(n)//1000 != 0:
            if num == np.inf or num == -np.inf:
                return str(num)
            e += 1
            n = n//10
            num/= 10
        if e != 0:
            return '%.2fe%i'%(num,e)
        else:
            return '%.2f'%(num)
    else:
        n = num
        e = 0
        while abs((n*1000))//1000 == 0.0:
            e -= 1
            n = n*10
            num*= 10
        if e != 0:
            return '%.2fe%i'%(num,e)
        else:
            return '%.2f'%(num)
        
def foiclicado(objeto,mouse):
    cx,cy = mouse.pos
    if cx >= objeto.x and cx <= objeto.x + objeto.width\
        and cy >= objeto.y and cy <= objeto.y + objeto.height:
        return True
    else:
        return False


def propclick(obj,mouse):
    cx,cy = mouse.pos
    if foiclicado(obj,mouse) == False:
        return None,None
    return (cx-obj.x)/(obj.x + obj.width),(cy-obj.y)/(obj.y + obj.height)
    


class botao_blbaixo(Button):
    def __init__(self,blbaixo,pai,**args):
        super().__init__(on_release = self.on_release_,
                         **args)
        blbaixo.add_widget(self)
        self.pai = pai

    def on_release_(self,*args):
        if self.background_color == [1,1,1,1]:
            self.background_color = [0,0,1,1]
            self.funcao1(*args)
        else:
            self.background_color = [1,1,1,1]
            self.funcao2(*args)

    def funcao1(self,*args):
        pass

    def funcao2(self,*args):
        pass



class scroll(BoxLayout):
    def __init__(self,lista,**args):
        super().__init__(**args)
        
        self.sv = ScrollView(size_hint_x = None,
                             size_hint_y = None,
                             size = self.size)
        self.sv.add_widget(self)
        self.lista = lista
        self.cria()

##    def on_touch_down(self,*args):
##        if self.collide_point(args[0].x,args[0].y) == True:
##            self.clicked = args[0].x
##            self.size0 = self.size[0]
##            #print(args[0].x,args[0].y)
##            #print(self.pos,self.size)
##        else:
##            on_release(*args)
##
##    def on_touch_move(self,*args):
##        if self.collide_point(args[0].x,args[0].y) != 23:
##            print(self.pos)
##            #(100,Window.size[1])
##            self.size = (self.size0 + self.clicked - args[0].x,self.size[0])
##            self.sv.size = (self.size0 + self.clicked - args[0].x,self.size[0])

    def adiciona(self,obj):
        
        xp,yp = obj.size
        x,y = self.size
        x += xp
        y += yp
        self.lista.append(obj)
        self.add_widget(obj)
    

    def cria(self):
        l = [i for i in self.children]
        for i in l:

            if 'desfazer' in i.__dict__ and i.desfazer == True\
               and i not in self.lista:
                #if i.background_color == [0,0,1,1]:
                try:
                    i.funcao_desfazer()
                except Exception as ex:
                    print('desfazer erro: ',ex)
            self.remove_widget(i)

        x = 0
        y = 0
        for i in self.lista:
            xp,yp = i.size
            x += xp
            y += yp
            self.add_widget(i)

    
        if self.orientation == 'vertical':
            self.size = (self.size[0],y)

            self.sv.size = (self.size[0],Window.size[1])

        else:

            self.size = (x,self.size[1])

            self.sv.size = (Window.size[0],self.size[1])

    
        
        
class botao_cor(Button):
    def __init__(self,bl = None,**args):
        super().__init__(on_release = self.muda_cor,**args)
        if bl != None:
            bl.add_widget(self)
    def muda_cor(self,*args):
        if self.background_color == [1,1,1,1]:
            self.funcao1(*args)
            self.background_color = [0,0,1,1]
            
        else:
            self.funcao2(*args)
            self.background_color = [1,1,1,1]
            

    def funcao1(self,*args):
        pass

    def funcao2(self,*args):
        pass

class botaoti(BoxLayout):
    def __init__(self,orientacao = 'vertical',dicbl = {},dicbt = {},
                 dicti = {}):
        super().__init__(orientation = orientacao,**dicbl)
        bl = self
        ti = TextInput(**dicti)
        bt = Button(**dicbt)
        bl.add_widget(bt)
        bl.add_widget(ti)
        self.bl = bl
        self.ti = ti
        self.bt = bt

class labelti(BoxLayout):
    def __init__(self,orientacao = 'vertical',dicbl = {},diclb = {},
                 dicti = {}):

        super().__init__(orientation = orientacao,**dicbl)
        bl = self
        ti = TextInput(**dicti)
        lb = Label(**diclb)
        bl.add_widget(lb)
        bl.add_widget(ti)
        self.bl = bl
        self.ti = ti
        self.lb = lb
        

import os

class modelo(App):
    def __init__(self,fig = None,ax = None,**args):
        print('carregando modelo')
        super().__init__()
        if fig == None:
            self.figura,self.ax = plt.subplots()
            self.fig = self.figura
        else:
            self.figura = fig; self.fig = fig
            self.ax = fig.axes[0]
            
        figura = FigureCanvasKivyAgg(self.figura)
            
        self.bl = BoxLayout()
        self.bl_figura = BoxLayout()
        self.bl_figura.on_touch_down = self.on_touch_down
        self.bl_figura.on_touch_move = self.on_touch_move
        self.bl_figura.on_touch_up = self.on_touch_up
        self.size_blbaixo = 50
        #Text input em baixo
        self.ti_baixo = TextInput(size_hint_y = None,size = (0,35),
                                  multiline = False)
        self.bl_baixo = BoxLayout(size_hint_y = None,size = (0,self.size_blbaixo))
        self.bl_lateral = scroll([],size_hint_y = None,
                                 size_hint_x = None,
                                 size = (200,Window.size[1]-self.size_blbaixo),
                                    orientation = 'vertical')

        x,y = self.bl.size
       

        baux = BoxLayout(orientation = 'vertical')
        baux.add_widget(self.bl_figura)
        baux.add_widget(self.ti_baixo)
        baux.add_widget(self.bl_baixo)
        self.bl.add_widget(baux)
        self.bl.add_widget(self.bl_lateral.sv)

        self.bl_figura.add_widget(figura)


        self.blupa = Button(text =  'zoom',on_release = self.lupa)
        self.breszoom = Button(text = 'rz',on_release = self.res_zoom)
        self.bsel = Button(text = 'sel',on_release = self.func_bsel)
        baux3 = BoxLayout(size_hint_x = None, size = (50,0))
        baux2 = BoxLayout(orientation = 'vertical', size_hint_x = None, size = (50,0))
        baux3.add_widget(self.bsel)
        baux2.add_widget(self.blupa)
        baux2.add_widget(self.breszoom)
        self.bl_baixo.add_widget(baux2)
        self.bl_baixo.add_widget(baux3)

        self.ti_ponto = TextInput(size_hint_x = None,size = (150,0))
        self.bl_baixo.add_widget(self.ti_ponto)
        
        self.ti_size_bl_baixo = TextInput(on_text_validate = self.set_size_blbaixo,
                                          size_hint_x = None, size = (50,0),
                                          multiline = False, text = str(self.bl_lateral.size[0]))
        
        
        self.bl_baixo.add_widget(self.ti_size_bl_baixo)
                                 
        self.baux2 = baux2
        self.baux3 = baux3

        self.selecao_ = False

        self.fix_ax = False

    def set_size_blbaixo(self,*args):
        try:
            x,y = self.bl_lateral.size
            self.bl_lateral.size = (eval(args[0].text),y)
            self.bl_lateral.cria()
        except Exception as ex:
            self.ti_baixo.text = str(ex)

    def foiclicado(self,objeto,mouse):
        cx,cy = mouse.pos
        if cx >= objeto.x and cx <= objeto.x + objeto.width\
           and cy >= objeto.y and cy <= objeto.y + objeto.height:
            return True
        else:
            return False

    def foiclicado_ax(self,ax,mouse):
        x,y = mouse.pos
        a = ax.get_window_extent()

        xcima = a.x0 + self.bl_figura.x
        xbaixo = a.x1 +  self.bl_figura.x
        ycima = a.y0 + self.bl_figura.y
        ybaixo = a.y1 + self.bl_figura.y
        if x < xbaixo and x > xcima and y < ybaixo and y > ycima:
            return True
        else:
            return False
        
    def res_zoom(self,*args):
        try:
            if len(self.ax.images) > 0:
                shape = self.ax.images[-1].get_array().shape
                self.ax.set_xlim(-0.5,shape[1]-0.5)
                if self.ax.images[-1].origin!= 'Upper':
                    self.ax.set_ylim(shape[0],0)
                else:
                    self.ax.set_ylim(0,shape[0])
                self.atualiza()
                return
            
            x,y = [],[]
            for l in self.ax.lines:
                lx,ly = l.get_data()
                if len(lx) != 0:
                    x.append(max(lx))
                    x.append(min(lx))
                    y.append(max(ly))
                    y.append(min(ly))
                for p in self.ax.patches:
                    x.append(p.get_x())
                    x.append(p.get_x() + p.get_width())
                    y.append(p.get_y())
                    y.append(p.get_height() + p.get_y())
                    
            x = np.array(x)
            y = np.array(y)
            

            y = y[(y>-np.inf) & (y<np.inf)]
            x = x[(x>-np.inf) & (x<np.inf)]
            xmin = x.min(); xmax = x.max()
            ymin = y.min(); ymax = y.max()

##
##            for i in self.ax.lines[1:]:
##                x,y = i.get_data()
##                    #print(x,y)
##                xmin,xmax = self.atualiza_limites(x,(xmin,xmax))
##                ymin,ymax = self.atualiza_limites(y,(ymin,ymax))

            extra_x = abs(xmin - xmax)*0.1
            extra_y = abs(ymin - ymax)*0.1
            self.ax.set_xlim((xmin-extra_x,xmax + extra_x))
            self.ax.set_ylim((ymin- extra_y,ymax + extra_y))
            self.fig.canvas.draw()
        except Exception as ex:
            print(ex)


    def lupa(self,*args):
        if args[0].color == [1,1,1,1]:
            args[0].color = [0,0,1,1]
        else:
            args[0].color = [1,1,1,1]


    def mouse2valor(self,px,py,xlim,ylim):
        
        a = self.ax.get_window_extent()

        xcima = a.x0 + self.bl_figura.x; xbaixo = a.x1 +  self.bl_figura.x
        ycima = a.y0 + self.bl_figura.y; ybaixo = a.y1 + self.bl_figura.y

        a,b = xlim
        
        if self.ax.get_xscale() == 'linear':
            dddp = (b-a)/(xbaixo-xcima) #distancia/pixel
            npixels = (px-xcima) #numero de pixels
            x = a + dddp*npixels
        if self.ax.get_xscale() == 'log':
            a = np.log10(a); b = np.log10(b)
            dddp = (b-a)/(xbaixo-xcima) #distancia/pixel
            npixels = (px-xcima) #numero de pixels
            x = 10**(a + dddp*npixels)
        a,b = ylim
        if self.ax.get_yscale() == 'log':
            a = np.log10(a); b = np.log10(b)
            dddp = (b-a)/(ybaixo-ycima) #distancia/pixel
            npixels = (py-ycima) #numero de pixels            
            y = 10**(a + dddp*npixels)
        if self.ax.get_yscale() == 'linear':
            dddp = (b-a)/(ybaixo-ycima) #distancia/pixel

            npixels = (py-ycima) #numero de pixels            
            y = a + dddp*npixels
        
        return x,y

    def func_bsel(self,*args):
        if self.bsel.color == [1,1,1,1]:
            self.bsel.color = [0,0,1,1]
            l = self.line_selecao = self.ax.plot([],[] ,'--',
                                               color = 'yellow')[0]
            l.set_lw(0.5)
        else:
            self.bsel.color = [1,1,1,1]
            self.apaga_selecao()
            
    def clique_duplo(self,*args):
        pass
            
    def desce(self,*args):
        self.px,self.py = args[0].pos
        if 'ultimo_clique' in self.__dict__ \
            and abs(time()-self.ultimo_clique) <= 0.2:
            if self.ultimo_clique_botao == args[0].button:
                clique_duplo = True
            else:
                clique_duplo = False
        else:
            clique_duplo = False
        self.ultimo_clique = time()
        self.ultimo_clique_botao = args[0].button
        propx,propy = propclick(self.bl_figura,args[0])

        if self.fix_ax == False and propx != None:
            if propx > 0.5 and 'twinx_ax' in self.ax.__dict__ and self.ax.twinx_ax != None:
                self.ax = self.ax.twinx_ax
                print(self.ax)
            if propx < 0.5 and 'parent_ax' in self.ax.__dict__:
                self.ax = self.ax.parent_ax
                print(self.ax,'parent')
        if clique_duplo == True:
            self.clique_duplo(*args)

        try:

            self.xl1,self.xl2 = self.ax.get_xlim()
            self.yl1,self.yl2 = self.ax.get_ylim()

            self.px,self.py = args[0].pos
            pontox,pontoy = self.mouse2valor(self.px,self.py,(self.xl1,self.xl2),
                                             (self.yl1,self.yl2))

                

            texto = 'x: %s\ny: %s'%(num2e(pontox),
                                                     num2e(pontoy),)
            
            self.ti_ponto.text = (texto)

            
            self.ptx = pontox; self.pty = pontoy
            self.ptx2 = pontox; self.pty2 = pontoy


        except Exception as ex:
            self.ax.set_title(str(ex))
            print(ex,ex.__traceback__.tb_lineno)

    def cria_selecao(self,*args):
        

        self.line_selecao.set_data([self.ptx,self.ptx2,self.ptx2,self.ptx,
                            self.ptx],
                            [self.pty,self.pty,self.pty2,self.pty2,
                            self.pty])
        self.figura.canvas.draw()
        self.selecao_ = True



    def apaga_selecao(self,*args):

        if 'line_selecao' in self.__dict__:
            self.ax.lines.remove(self.line_selecao)
        self.selecao_ = False

    def move_(self,*args):
        if self.foiclicado(self.bl_figura,args[0]) == False:
            print("Clique fora")
            return
        try:
            px,py = args[0].pos
            pontox,pontoy = self.mouse2valor(px,py,self.ax.get_xlim(),
                                             self.ax.get_ylim())
            self.ptx2 = pontox; self.pty2 = pontoy
        except:
            pass

    def move(self,*args):
        if self.foiclicado(self.bl_figura,args[0]) == False:
            print("Clique fora")
            return
        try:
            px,py = args[0].pos
            pontox,pontoy = self.mouse2valor(px,py,self.ax.get_xlim(),
                                             self.ax.get_ylim())
            self.ptx2 = pontox; self.pty2 = pontoy

            
            if self.blupa.color == [0,0,1,1]:
                self.cria_selecao()
            elif self.bsel.color == [0,0,1,1]:
                self.cria_selecao()

            else:

                #corrigir primeiro o ponjto
                if self.ax.get_xscale() == 'linear':
                    fx = lambda x: x
                    fx2 = fx
                if self.ax.get_xscale() == 'log':
                    fx = np.log10
                    fx2 = lambda x: 10**x
                if self.ax.get_yscale() == 'linear':
                    fy = lambda x: x
                    fy2 = fy
                if self.ax.get_yscale() == 'log':
                    fy = np.log10
                    fy2 = lambda x: 10**x
                    
                # se for log converter para o expoente de
                #depois elevar 
                pontox,pontoy = self.mouse2valor(px,py
                                        ,(self.xl1,self.xl2),
                                    (self.yl1,self.yl2))

                dx = fx(self.ptx) - fx(pontox)
                dy = - fy(pontoy) + fy(self.pty)
                    
                
                if args[0].button == 'left':
                    

                    self.ax.set_xlim(fx2(fx(self.xl1) + dx),
                                          fx2(fx(self.xl2) + dx))
                    self.ax.set_ylim(fy2(fy(self.yl1) + dy),
                                          fy2(fy(self.yl2) + dy))
                    self.figura.canvas.draw()
                else:
                    l = self.ax.images
                    
                    ylim = self.ax.get_ylim()
                    if ylim[1] > ylim[0] and len(l) == 0:

                                       
                        self.ax.set_xlim(fx2(fx(self.xl1) - dx),
                                              fx2(fx(self.xl2) + dx))

                        self.ax.set_ylim(fy2(fy(self.yl1) - dy),
                                              fy2(fy(self.yl2) + dy))



                    if len(l) != 0:
                        d = -dx
                        
                        x1,x2 = self.ax.get_xlim()
                        y1,y2 = self.ax.get_ylim()
                        
                        prop = d/abs(x2-x1)
                        DX = (x2-x1)*prop
                        DY = (y2-y1)*prop

                        if int(abs(x1-x2)/(x1-x2)) != int(abs(x1+DX - (x2-DX))/(x1+DX - (x2-DX))):
                            return
                        if int(abs(y1-y2)/(y1-y2)) != int(abs(y1+DY - (y2-DY))/(y1+DY - (y2-DY))):
                            return

                        self.ax.set_xlim(x1 + DX, x2- DX)
                        self.ax.set_ylim(y1 + DY, y2 - DY)

                        
                    self.figura.canvas.draw()
        except Exception as ex:
            print(ex,ex.__traceback__.tb_lineno)

    def sobe(self,*args):
        if self.foiclicado(self.bl_figura,args[0]) == False:
            #print("Clique fora")
            return
        try:
        
            if self.blupa.color == [0,0,1,1]:
                ylim = self.ax.get_ylim()
                self.set_xlim(self.ptx,self.ptx2)
                if ylim[1] >= ylim[0]:
                    self.set_ylim(self.pty,self.pty2)
                else:
                    self.set_ylim(self.pty2,self.pty)
                self.px1, self.px2 = self.ax.get_xlim()
                self.py2, self.py1 = self.ax.get_ylim()

                if 'line_selecao' in self.__dict__:
                    self.ax.lines.remove(self.line_selecao)
                        
        except Exception as ex:
            print(ex,ex.__traceback__.tb_lineno)


    def on_touch_down(self,*args):
        self.desce(*args)

    def on_touch_move(self,*args):
        self.move(*args)

    def on_touch_up(self,*args):
        self.sobe(*args)

        
    def build(self):
        return self.bl

    def compila(self,file,nome):
        import compila
        import os
        pasta = os.getcwd()
        arq = open(file)
        s = arq.read()
        arq.close()
        arq = open('provisorio____com.py','w')
        s = 'import os\nos.chdir("%s")\nCOMPILADO = True\n'%pasta + s
        arq.write(s)
        compila.compila('provisorio____com.py')
        os.system('mv provisorio____com.pyc  %s.pyc'%nome)
        arq.close()
        os.system('rm provisorio____com.py')

#modelo().run()

