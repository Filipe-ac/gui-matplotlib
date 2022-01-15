from kivyplt import *
from kivy.config import Config
Config.set('kivy', 'exit_on_escape', '0')
from funcoes import *
from numpy import nan,array,ndarray,float64
from time import time
from fp_load import *

class botao_deleta(Button):
    def __init__(self,funcao,**args):
        super().__init__(**args)
        self.funcao = funcao


    def on_release(self,clock = False,*args):
 
        if self.background_color == [1,1,1,1]:
            self.background_color = [1,0,0,1]
            self.clock = Clock.schedule_once(lambda *args : self.on_release(clock = True)
                                             , 0.5)
                
            return
        else:
            if clock == True:
                self.background_color = [1,1,1,1]
                return
                    
        self.clock.cancel()
        self.funcao(*(self,))
        self.background_color = [1,1,1,1]


class fslider(Slider):
    def __init__(self,minimo,maximo,valor,**args):
        super().__init__(min = 0, max = 1,step = 1e-10,**args)
        
        self.maximo = maximo
        self.minimo = minimo
        self.valor = valor
        self.set_value()

        #print(self.maximo,self.minimo,self.valor,self.min,self.max,'\n')
        
    def get_valor(self,*args):
        self.valor = self.value*(self.maximo-self.minimo) + self.minimo
        #print(self.value,self.valor)
        return self.valor

    def set_value(self,*args):
        #self.get_valor()
        if self.maximo != self.minimo:
            #print((self.valor - self.minimo)/(self.maximo - self.minimo),'valor')
            self.value = float('%.6f'%((self.valor - self.minimo)/(self.maximo - self.minimo)))
        else:
            self.value = 0
    def set_valor(self,valor,*args):
        self.valor = valor
        if valor > self.maximo:
            self.maximo = valor
        if valor < self.minimo:
            self.minimo = valor
        self.set_value()
    def set_maximo(self,maximo,*args):
        self.maximo = maximo
        self.set_value()
    def set_minimo(self,minimo,*args):
        self.minimo = minimo
        self.set_value()



class lateral_menu(Button):
    def __init__(self,pai,bl = None,**args):
        super().__init__(**args)
        self.pai = pai
        self.on_touch_down = self.muda_cor
        self.on_touch_move = self.muda_cor2
        if bl != None:
            bl.add_widget(self)
        self.bl = bl
        self.time = time()

    def add_methods(self,obj,lst):
        for i in lst:
            self.labelti_attr(obj,get2set(i),
                              eval('self.obj.%s()'%i),
                                                 label_att = True)
        
    def label(self,text = '',**args):
        lb = Label(text = text,**args)
        self.pai.bl_lateral.lista.append(lb)
        return lb

    def funcao_desfazer(self,*args):
        self.pai.double_click = True
        self.pai.fix_ax = False
        self.pai.bl_figura.on_touch_down = self.pai.on_touch_down
        self.pai.bl_figura.on_touch_move = self.pai.on_touch_move
        self.pai.bl_figura.on_touch_up = self.pai.on_touch_up
        
    def atribute_arg_labelti(self,obj):
        '''return the atribute and argumento for a text input obj
            for the forms att,arg or atribute in the Label,
            and argument in the TextInput'''
        
        if obj.att_and_arg == True:
            l = obj.text.split(',')
            atributo,valor = l[0],','.join(l[1:])
        else:
            atributo = obj.label.text
            valor = obj.text
        return atributo,valor

    def muda_cor2(self,*args):
        if self.collide_point(args[0].x,args[0].y) == True:
            if time()-self.time > 1:
                self.muda_cor(*args)
                self.time = time()
            else:
                pass


    def muda_cor(self,*args):

        
        if len(args) > 0 and self.collide_point(args[0].x,args[0].y) == True\
        or len(args) == 0:
            if len(args) == 0 or args[0].button == 'left':
                if self.background_color == [1,1,1,1]:
                    self.background_color = [0,0,1,1]
                    self.funcao1(*args)

                elif self.background_color == [1,0,0,1]:
                    self.background_color = [0,0,1,1]
                    self.funcao2d(*args)
                    self.funcao1(*args)
                    
                else:
                    self.funcao2(*args)
                    self.background_color = [1,1,1,1]
                    
            if len(args) != 0 and args[0].button == 'right':
                if self.background_color == [1,1,1,1]:
                    self.background_color = [1,0,0,1]
                    self.funcao1d(*args)

                elif self.background_color == [0,0,1,1]:
                    self.background_color = [1,0,0,1]
                    self.funcao2(*args)
                    self.funcao1d(*args)
                    
                else:
                    self.funcao2d(*args)
                    self.background_color = [1,1,1,1]
            
            

    def funcao1(self,*args):
        self.lista_original = self.pai.bl_lateral.lista.copy()
        self.pai.bl_lateral.cria()
        
    def funcao2(self,*args):
        self.pai.bl_lateral.lista = self.lista_original.copy()
        self.pai.bl_lateral.cria()
                

    def funcao1d(self,*args):
        pass
        
    def funcao2d(self,*args):
        pass


    def labelti_attr(self,obj,textolb = 'obj.',
                     textoti = '',
                     altura = 30,
                     label_att = False):

        if label_att == False:
            funcao = self.__set_attr__
        else:
            funcao = self.__set_attr_lbti__
            
        textolb = str(textolb)
        textoti = str(textoti)
        bl = BoxLayout(orientation = 'vertical',
                       size_hint_y = None,
                       size = (0,2*altura))
        lb = Label(text = textolb,
                            size_hint_y = None,
                            size = (0,altura))
        bl.add_widget(lb)
        ti = TextInput(text = textoti,
                                size_hint_y = None,
                                size = (0,altura),
                                multiline = False,
                                on_text_validate = funcao)
        ti.label = lb
        bl.add_widget(ti)
        ti.obj = obj        
        self.pai.bl_lateral.lista.append(bl)
        return ti

    def __set_attr_lbti__(self,*args):
        text = args[0].text
        obj_list = args[0].obj
        method = args[0].label.text
        valor = args[0].text
        if type(obj_list) != list:
            obj_list = [obj_list]
        for obj in obj_list:
            try:
                try:
                    eval('obj.%s(%s)'%(method,valor))
                    print('obj.%s(%s)'%(method,valor))
                except:
                    eval('obj.%s("%s")'%(method,valor))
                    print('obj.%s("%s")'%(method,valor))
                self.pai.fig.canvas.draw()
            except Exception as ex:
                self.pai.ti_baixo.text = str(ex)
        
    def __set_attr__(self,*args):
        text = args[0].text
        obj_list = args[0].obj

        if type(obj_list) != list:
            obj_list = [obj_list]
        for obj in obj_list:
            try:
                try:
                    eval('obj.%s'%text)
                    print('obj.%s'%text)
                except:
                    eval('obj.%s'%text)
                    print('obj.%s'%text)
                self.pai.fig.canvas.draw()
            except Exception as ex:
                self.pai.ti_baixo.text = str(ex)

        

    def labeltislider(self,chave,dic,funcao,
                      textolb,textoti,valor = 0.5,
                      altura = 30,alturas = 80,
                      lim1 = -np.inf, lim2 = np.inf):

        ''' Controla a variavel (chave) dentro do dicionario (dic) e chama a funcao aplicando
            o dic como kwargs (funcao(**dic))'''

        #retorna o BoxLayout contento o Label, TextInput com calor do slider,
            # e dois TI com limites do slider


        slider = fslider(minimo = lim1,maximo = lim2, valor = valor,
                         size_hint_y = None,
                             size = (0,alturas),
                             on_touch_move = self.aplica_slider)

        slider.dic = dic
        slider.chave = chave
        self.funcao_slider = funcao
        

        bl = BoxLayout(orientation = 'vertical',
                       size_hint_y = None,
                       size = (0,3*altura + alturas))
        bl.add_widget(Label(text = textolb,
                            size_hint_y = None,
                            size = (0,altura)))
        ti = TextInput(text = textoti,
                                size_hint_y = None,
                                size = (0,altura),
                                multiline = False,
                                on_text_validate = self.aplica_slider)
        ti.chave = chave
        ti.funcao = funcao
        ti.dic = dic
        
        sx = self.pai.bl_lateral.size[0]

        tilim1 = TextInput(text = str(lim1),
                                size_hint_y = None,
                           size_hint_x = None,
                                size = (sx/2,altura),
                                multiline = False,
                                on_text_validate = self.funcao_lim_slider)

        tilim2 = TextInput(text = str(lim2),
                                size_hint_y = None,
                           size_hint_x = None,
                                size = (sx/2,altura),
                                multiline = False,
                                on_text_validate = self.funcao_lim_slider)

        tilim1.tipo = 'minimo'; tilim1.slider = slider
        tilim2.tipo = 'maximo'; tilim2.slider = slider
        slider.ti = ti
        ti.slider = slider
        
        bl.add_widget(ti)

        bl2 = BoxLayout(orientation = 'horizontal',
                       size_hint_y = None,
                       size = (0,1*altura))
        bl2.add_widget(tilim1)
        bl2.add_widget(tilim2)
        bl.add_widget(bl2)
    
        bl.add_widget(slider)
        bl.slider = slider
        
        self.pai.bl_lateral.lista.append(bl)
        return bl

    def atualiza_labeltislider(self,bl,
                               valor = None,
                               lim1 = None,
                               lim2 = None):

        #print(bl.children)
        slider = bl.children[0]
        ti = bl.children[2]
        ti1 = bl.children[1].children[0]
        ti2 = bl.children[1].children[1]
        
        if valor != None:
            slider.set_valor(valor)
            ti.text = '%.6f'%valor
        if lim1 != None:
            slider.set_minimo(lim1)
            ti1.text = str(lim1)
        if lim2 != None:
            slider.set_maximo(lim2)
            ti2.text = str(lim2)
            

    def funcao_lim_slider(self,*args):
        try:
            if args[0].tipo == 'minimo':
                args[0].slider.set_minimo(eval(args[0].text))
            if args[0].tipo == 'maximo':
                args[0].slider.set_maximo(eval(args[0].text))
        except Exception as ex:
            pass

    def aplica_slider(self,*args):
        #args[0] = slider ou TextInput
        if 'ti' in args[0].__dict__:
            #se for Slider:
            if foiclicado(args[0],args[1]) == False:
                return
            args[0].ti.text = '%.6f'%args[0].get_valor()
            valor = args[0].get_valor()
            
        if 'slider' in args[0].__dict__:
            #se for o TextInput
            try:
                args[0].slider.set_valor(eval(args[0].text))
                valor = eval(args[0].text)
            except:
                valor = args[0].text
                
        args[0].dic[args[0].chave] = valor
        self.funcao_slider()
            

    def botaoti(self,funcao,textolb,textoti,altura = 30):

        bl = BoxLayout(orientation = 'vertical',
                       size_hint_y = None,
                       size = (0,2*altura))
        botao = Button(text = textolb,
                            size_hint_y = None,
                            size = (0,altura),
                      on_release = funcao)
        bl.add_widget(botao)
        ti = TextInput(text = textoti,
                                size_hint_y = None,
                                size = (0,altura))
        bl.add_widget(ti)
        botao.ti = ti
        self.pai.bl_lateral.lista.append(bl)
        
    def labelti(self,funcao,textolb,textoti,altura = 30,
                att_and_arg = True):
        textolb = str(textolb)
        textoti = str(textoti)
        bl = BoxLayout(orientation = 'vertical',
                       size_hint_y = None,
                       size = (0,2*altura))
        lb = Label(text = textolb,
                            size_hint_y = None,
                            size = (0,altura))
        bl.add_widget(lb)
        ti = TextInput(text = textoti,
                                size_hint_y = None,
                                size = (0,altura),
                                multiline = False,
                                on_text_validate = funcao)
        ti.label = lb
        ti.att_and_arg = att_and_arg
        bl.add_widget(ti)
        
        self.pai.bl_lateral.lista.append(bl)
        return ti

    def labelti_cols(self,funcoes,textolb,textoti,altura = 30,
                     att_and_args = True):
        if type(funcoes) != list:
            funcoes = [funcoes for i in textolb]
        if type(att_and_args) != list:
            att_and_args = [att_and_args for i in textolb]
        lista = []
        largura = self.pai.bl_lateral.width/len(textolb)
        
        BL = BoxLayout(orientation = 'horizontal',
                       size_hint_y = None,
                       size = (0,2*altura))
        
        for i in range(len(textolb)):

            bl = BoxLayout(orientation = 'vertical',
                           size_hint_y = None,
                           size_hint_x = None,
                           size = (largura,2*altura))
            lb = Label(text = textolb[i],
                                size_hint_y = None,
                           size_hint_x = None,
                           size = (largura,altura))
            bl.add_widget(lb)
            ti = TextInput(text = textoti[i],
                                    size_hint_y = None,
                                    size_hint_x = None,
                                    size = (largura,altura),
                                    multiline = False,
                                    on_text_validate = funcoes[i])
            ti.label = lb
            ti.att_and_arg = att_and_args[i]
            bl.add_widget(ti)
            lista.append(ti)
            BL.add_widget(bl)
        self.pai.bl_lateral.lista.append(BL)
        return lista

    def insere_botao(self,funcao,texto,altura = 30):
        botao = Button(text = texto,
                            size_hint_y = None,
                            size = (0,altura),
                      on_release = funcao)
        self.pai.bl_lateral.lista.append(botao)
        return botao
    
    def cria(self,*args):
        self.lista_original = [i for i in self.pai.bl_lateral.lista]
        self.pai.bl_lateral.lista = [self]
        
    def destroi(self,*args):
        if 'lista_original' not in self.__dict__:
            self.lista_original = []
        self.pai.bl_lateral.lista = [i for i in self.lista_original]
        self.pai.bl_lateral.cria()

    def _delete(self,*args):
        if self in self.pai.bl_lateral.lista:
            self.pai.bl_lateral.lista.remove(self)
        if self in self.lista_original:
            self.lista_original.remove(self)
        self.destroi()

    def new_list(self,add_self = False,*args):
        self.lista_original = self.pai.bl_lateral.lista.copy()
        if add_self == False:
            self.pai.bl_lateral.lista = []
        else:
            self.pai.bl_lateral.lista = [self]

