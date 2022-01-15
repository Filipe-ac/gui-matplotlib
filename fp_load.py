from fplot3 import *
from matplotlib.colorbar import _ColorbarAutoLocator
plt.switch_backend('TkAgg')

#load_lists: get/set methods
#load_list_gui: attributes (obj.attr) may or may not native from matplotlib

def get2set(string):
    l = string.split('_')
    if string[0] == '_':
        ind = 1
    else:
        ind = 0
    l[ind] = l[ind].replace('get','set')
    return '_'.join(l)

#methods that return native python types (bool, int, str..)
ax_load_list = ['get_xlim','get_ylim',
                'get_yscale','get_xscale',
                'get_xlabel','get_ylabel',
                'get_alpha','get_aspect',
                'get_autoscale_on',
                'get_autoscalex_on', 'get_autoscaley_on',
                'get_label','get_visible']

ax_load_list_gui = ['id','axes_travados_x','axes_travados_y']

line_load_list = ['get_color',
                  'get_label','get_linestyle',
                  'get_linewidth','get_marker',
                  'get_markersize',
                  'get_visible','get_alpha',
                  'get_markeredgecolor',
                  'get_markeredgewidth',
                  'get_markerfacecolor']

line_load_list_gui = ['conteiner','original_data',
                      'funcao_eixox','funcao_eixoy',
                      'ratiox','ratioy','deltax','deltay',
                      'suavisa','window_lenght','polyorder',
                      'argsort','fits_curvas','nome_fit',
                      'plot_funcao','df_err','id','list_erry',
                      'list_errx','ax_ids']

axis_load_list = ['get_alpha','get_label_position']

text_load_list = ['get_alpha','get_color','get_fontsize','get_fontstyle',
                  'get_rotation','get_position','get_text',
                  'get_visible','get_label']
text_load_list_gui = ['conteiner']

img_load_list = ['get_alpha','get_visible',
                 'get_label','get_interpolation',
                 'get_clim']
img_load_list_gui = ['origin','regua1','regua2','unidade',
                     'line_regua_name','rotate_angle',
                     'array_original']

legend_load_list = ['get_alpha','get_visible','_get_loc']
legend_load_list_gui = ['shadow']

quadmesh_load_list = ['get_alpha']
quadmesh_load_list_gui = ['_meshWidth','_meshHeight','_coordinates']

label_load_list = ['get_text','get_color','get_fontsize','get_alpha',
                   'get_rotation']

patche_load_list = ['get_edgecolor','get_facecolor',
                    'get_ls','get_lw','get_label',
                    'get_alpha','get_visible',
                    'get_x','get_y','get_width',
                    'get_height']

polycollection_load_list = ['get_visible','get_linewidths','get_facecolors',
                            'get_edgecolors',
                            'get_alpha','get_label',
                            'get_linestyles','get_offset_position']


polycollection_load_list_gui = ['id','tipo','original_data']

def load_obj_default(obj,dic,obj_load_list,obj_load_list_gui = []):
    if obj == None:
        return None
    for i in obj_load_list:
        if i in dic:
            if (get2set(i) == i.replace('get_','set_')) == 0:
                print(i,get2set(i),i.replace('get_','set_'))
            getattr(obj,i.replace('get_','set_'))(dic[i])
    for i in obj_load_list_gui:
        if i in dic:
            obj.__dict__[i] = dic[i]
    return obj

def create_dict_default(obj,obj_load_list,obj_load_list_gui = []):
    if obj == None:
        return None
    dic = {i : getattr(obj,i)() for i in obj_load_list}
    
    for i in obj_load_list_gui:
        if i in obj.__dict__:
            dic[i] = obj.__dict__[i]
    return dic

def name_ax(ax):
    if ax.get_label() == '':
        n = 1
        while 'ax%i'%n in [i.get_label() for i in ax.figure.axes]:
            n += 1
        ax.set_label('ax%i'%n)
        
def find_twin_ax(axes):
    '''return a list of unique axes and the twin axes as an atrribute'''
    #i think this function could be more compact
    df = pd.DataFrame(columns = ['rect'])
    for ax in axes:
        bbox = ax.get_position()
        t = [bbox.x0,bbox.y0,bbox.width,bbox.height]
        df.loc[ax] = str(t)

        
    df = df.reset_index().set_index('rect')

    list_axes = []
    for ind in df.index.unique():
        if len(df.loc[ind]) != 1:
            l_axes = [i[0] for i in df.loc[ind].values]
            #decide wich one is the principal, the twinx and the twiny
            df_axes = pd.DataFrame(index = l_axes,columns = ['xaxis_pos',
                                                             'yaxis_pos'])
            
            for ax in l_axes:
                df_axes.loc[ax,'xaxis_pos'] = ax.xaxis.get_ticks_position()
                df_axes.loc[ax,'yaxis_pos'] = ax.yaxis.get_ticks_position()

            df_axes = df_axes.reset_index().set_index(['xaxis_pos','yaxis_pos'])
            main_ax = df_axes.loc['bottom','left']['index']
            name_ax(main_ax)
            
            if ('bottom','right') in df_axes.index:
                main_ax.twinx_ax = df_axes.loc['bottom','right']['index']
                main_ax.twinx_ax.parent_ax = main_ax
                main_ax.twinx_ax.set_label(main_ax.get_label() + '_' + 'y2')
            else:
                main_ax.twinx_ax = None
            if ('top','left') in df_axes.index:
                main_ax.twiny_ax = df_axes.loc['top','left']['index']
                main_ax.twiny_ax.parent_ax = main_ax
                main_ax.twiny_ax.set_label(main_ax.get_label() + '_' + 'x2')
            else:
                main_ax.twiny_ax = None
            list_axes.append(main_ax)
        else:
            ax = df.loc[ind].values[0]
            ax.twinx_ax = None
            ax.twiny_ax = None
            list_axes.append(ax)

    return list_axes

def find_colorbar_ax(axes):
    '''separete colorbar from regular axes'''
    list_cb = []; list_axes = []
    for ax in axes:
        for axis in [ax.xaxis,ax.yaxis]:
            if isinstance(axis.get_major_locator(),_ColorbarAutoLocator) == True:
                mappable = axis.get_major_locator()._colorbar.mappable
                if 'colorbar_ax' in mappable.__dict__:
                    mappable.colorbar_ax.append(ax)
                else:
                    mappable.colorbar_ax = [ax]
                list_cb.append(ax)
                
        if ax not in list_cb:      
            list_axes.append(ax)
        
    return list_cb,list_axes

def load_fig(fig_dict):
    print(fig_dict)
    if type(fig_dict) != dict:
        dic = {}

        #colorbar_ax
        #colorbar,#regular axes (load here just the regular ones)
        list_cb,list_axes = find_colorbar_ax(fig_dict.axes)
        print('cb',list_cb)
        print('\nax',list_axes)

        #axes
        dic['axes'] = []
        for ax in find_twin_ax(list_axes):
            if ax != None:
                dic['axes'].append(load_ax(ax))
        return dic
    else:
        fig = plt.figure()

        #axes
        for dict_ax in fig_dict['axes']:
            if dict_ax != None:
                load_ax(dict_ax,
                        fig.add_axes(matplotlib.transforms.Bbox(dict_ax['rect'])))

        #axes travados
        for ax in fig.axes:
            if 'axes_travados_x' in ax.__dict__:
                set_funcoes_acopladas(ax,ax.axes_travados_x,eixo = 'x')
            if 'axes_travados_y' in ax.__dict__:
                set_funcoes_acopladas(ax,ax.axes_travados_y,eixo = 'y')        
        return fig

def load_ax(ax_dict,ax = None,cbar = False):
    '''load a ax from a ax object or create
        a ax object from a dict'''
    if type(ax_dict) != dict:
        
        ax = ax_dict
        dic = create_dict_default(ax,ax_load_list,ax_load_list_gui)

        #rectangle
        bbox = ax.get_position()
                    #  left     bottom  width    height
        dic['rect'] = [[bbox.x0,bbox.y0],[bbox.x1,bbox.y1]]
        dic['size'] = bbox.size

        #lines
        dic['lines'] = []
        for line in ax.lines:
            dic['lines'].append(load_line(line))

        #twins
        if 'twinx_ax' in ax.__dict__:

            dic['twin_x'] = load_ax(ax.twinx_ax) if ax.twinx_ax != None else None
            dic['twin_y'] = load_ax(ax.twiny_ax) if ax.twiny_ax != None else None

        #images
        dic['images'] = [load_img(obj) for obj in ax.images]

        #collections
        dic['collections'] = [load_collection(obj) for obj in ax.collections]

        #legends
        dic['legend'] = create_dict_default(ax.get_legend(),
                                            legend_load_list,
                                            legend_load_list_gui)
        if dic['legend'] != None:
            dic['legend']['fontsize'] = ax.get_legend()._fontsize
            dic['legend']['framealpha'] = ax.get_legend().get_frame().get_alpha()

        #texts
        dic['texts']  = [load_text(obj) for obj in ax.texts]

        #bar
        dic['bars'] =  [load_bar(bar) for bar in ax.containers if isinstance(bar,BarContainer) == True]

        #axis
        dic['xaxis'] = load_axis(ax.xaxis)
        dic['yaxis'] = load_axis(ax.yaxis)

        
        return dic
            
    
    else:
            
        #rectangle
        bbox = matplotlib.transforms.Bbox(ax_dict['rect'])
        ax.set_position(bbox)


        #lines
        for line_dict in ax_dict['lines']:
            if 'data' not in line_dict:
                df = line_dict['original_data']
                line = ax.plot([],[])[0]
                line.set_dataf(df['x'].values,df['y'].values)
                load_line(line_dict,line)
            else:
                line = ax.plot([],[])[0]
                line.set_data(line_dict['data'][0],line_dict['data'][1])
                load_line(line_dict,line)        
        
        #twins
        if 'twin_x' in ax_dict:
            
            if ax_dict['twin_x'] != None:
                twinx = ax.twinx()
                load_ax(ax_dict['twin_x'],twinx)
            if ax_dict['twin_y'] != None:
                twiny = ax.twiny()
                load_ax(ax_dict['twin_y'],twiny)

        
        #images
        for img in ax_dict['images']:
            load_img(img,ax = ax)

        #collections
        if cbar == False:
            for col in ax_dict['collections']:
                load_collection(col,ax)

        #legends
        if ax_dict['legend'] != None:
            args = {i:ax_dict['legend'][i] for i in legend_load_list_gui}
            args['fontsize'] = ax_dict['legend']['fontsize']
            args['framealpha'] =  ax_dict['legend']['framealpha']
            leg = ax.legend(**args)
            load_obj_default(leg,ax_dict['legend'],legend_load_list)

        #texts
        if 'texts' in ax_dict:
            for obj in ax_dict['texts']:
                load_text(obj,ax)

        #bar
        if 'bars' in ax_dict:
            for bar in ax_dict['bars']:
                load_bar(bar,ax)
        ax = load_obj_default(ax,ax_dict,ax_load_list,ax_load_list_gui)

        #axis
        load_axis(ax_dict['xaxis'],ax.xaxis)
        load_axis(ax_dict['yaxis'],ax.yaxis)
    
        return ax

def load_collection(obj,ax = None):
    if type(obj) != dict:
        if isinstance(obj,matplotlib.collections.QuadMesh) == True:
            dic = load_quadmesh(obj)
            dic['obj'] = 'quadmesh'
            return dic
        if isinstance(obj,PolyCollection) == True:
            
            dic = load_polycollection(obj,ax)
            dic['obj'] = 'polycollection'
            return dic
        
    elif obj == None:
        return None
    
    else:
        cls = obj['obj']
        obj.__delitem__('obj')
        return eval('load_%s'%cls)(obj,ax)

def load_polycollection(obj,ax = None):
    if type(obj) != dict:
        dic = create_dict_default(obj,polycollection_load_list,
                                  polycollection_load_list_gui)

        #adiciona termos espurios (nao sei pq...) por isso o [1:]
        try:
            dic['verts'] = [obj.get_paths()[0].vertices[1:]]
        except:
            #para nao dar erro se estiver vazio
            dic['verts'] = []
        return dic
    else:
        pc = PolyCollection(obj['verts'])
        ax.add_collection(pc)
        
        load_obj_default(pc,obj,polycollection_load_list,
                         polycollection_load_list_gui)

                                  

def load_quadmesh(obj,ax = None):
    
    if type(obj) != dict:
        dic = create_dict_default(obj,quadmesh_load_list,quadmesh_load_list_gui)
        dic['array'] = obj.get_array()
        dic = load_cbar(obj,dic)
        return dic
    else:
        
        quad = QuadMesh(obj['_meshWidth'],obj['_meshHeight'],obj['_coordinates'])
        quad.set_array(obj['array'])
        quad = load_obj_default(quad,obj,quadmesh_load_list)
        load_cbar(obj,quad,ax)
        ax.add_collection(quad)
        

def load_line(line_dict,line = None):
    
    if type(line_dict) != dict:
        dic = create_dict_default(line_dict,line_load_list,
                                  line_load_list_gui)

        #data
    
        x,y = line_dict.get_data()
        dic['data'] = [x,y]

        return dic
    
    else:
        line = load_obj_default(line,line_dict,line_load_list,
                                line_load_list_gui)

        return line

def load_axis(obj,axis = None):
    
    if type(obj) != dict:
        dic = create_dict_default(obj,axis_load_list)

        #locator
        dic['locator'] = load_locator(obj.get_major_locator())

        #formatter
        dic['formatter'] = load_formatter(obj.get_major_formatter())

        #tick params
        dic['minor_params'] = obj._minor_tick_kw
        dic['major_params'] = obj._major_tick_kw

        #label
        dic['label'] = load_label(obj.get_label())
        
        return dic
    else:

        #tick params
        if 'major_params' in obj:
            axis.set_tick_params(which = 'major',**obj['major_params'])
            axis.set_tick_params(which = 'minor',**obj['minor_params'])
        
        #locator
        locator = load_locator(obj['locator'])
        if locator != None:
            
            axis.set_major_locator(locator)

        #formatter
        formatter = load_formatter(obj['formatter'])
        if formatter != None:
            axis.set_major_formatter(formatter)
            

        #label
        if 'label' in obj:
            l = load_label(obj['label'],axis.get_label())
 
        return load_obj_default(axis,obj,axis_load_list)

def load_locator(obj):
    '''decide what type of locattor is the obj'''
    if type(obj) != dict:
 
        if isinstance(obj,AutoLocator) == True:
            dic = load_autolocator(obj)
            dic['obj'] = 'autolocator'
            return dic
        elif isinstance(obj, _ColorbarAutoLocator) == True:
            dic = {}
            dic['obj'] = 'autolocator'
            return None
        elif isinstance(obj,FixedLocator) == True:
            dic = load_fixedlocator(obj)
            dic['obj'] = 'fixedlocator'
            return dic
        
    elif obj == None:
        return None
        
    else:
        cls = obj['obj']
        obj.__delitem__('obj')
        return eval('load_%s'%cls)(obj)

def load_formatter(obj):
    
    if type(obj) != dict:
        if isinstance(obj,FuncFormatter) == True:
            
            dic = load_funcformatter(obj)
            dic['obj'] = 'funcformatter'
            return dic
        if isinstance(obj,ScalarFormatter) == True:
            dic = load_scalarformatter(obj)
            dic['obj'] = 'scalarformatter'
            return dic
        if isinstance(obj,FixedFormatter) == True:
            dic = load_fixedformatter(obj)
            dic['obj'] = 'fixedformatter'
            return dic
        
    elif obj == None:
        return None
        
    else:
        cls = obj['obj']
        obj.__delitem__('obj')
        return eval('load_%s'%cls)(obj)

def load_funcformatter(obj):
    
    if type(obj) != dict:
        return {'string':obj.string}
    else:
        ff = FuncFormatter(**obj)
        return ff

def load_fixedformatter(obj):
    if type(obj) != dict:
        return {'seq':obj.seq}
    else:
        ff = FixedFormatter(**obj)
        return ff


def load_scalarformatter(obj):
    if type(obj) != dict:
        return {}
    else:
        return ScalarFormatter()

def load_fixedlocator(obj):
    if type(obj) != dict:
        dic = {}
        dic['locs'] = obj.locs
        return dic
    else:
        fl = FixedLocator(**obj)
        return fl

def load_autolocator(obj):
    if type(obj) != dict:
        dic = {}
        dic['nbins'] = obj._nbins
        return dic
    else:
        al = AutoLocator()
        al.set_params(**obj)
        return al


def load_cbar(obj,dic,ax = None):
    if type(obj) != dict:

        dic['cbar'] = []
        if 'colorbar_ax' in obj.__dict__:
            for cbar in obj.colorbar_ax:
                dic['cbar'].append(load_ax(cbar))
        dic['cmap'] = obj.get_cmap().name
        
        return dic
    else:
        #obj = dictionary; dic = mappable object
        dic.set_cmap(obj['cmap'])
        for cbar in obj['cbar']:
            cb = ax.figure.colorbar(dic)
            load_ax(cbar,cb.ax,cbar = True)


def load_img(obj,ax = None):
    if type(obj) != dict:
        dic = create_dict_default(obj,img_load_list,img_load_list_gui)
        
        dic['array'] = obj.get_array()
    
        #cbar
        dic = load_cbar(obj,dic)

        return dic
        

    else:
        img = ax.imshow(obj['array'],
                        origin = obj['origin'])
        
        img = load_obj_default(img,obj,img_load_list,img_load_list_gui)
        #rotacao
        if 'rotate_angle' in obj:
            ri = Image.fromarray(img.array_original).rotate(obj['rotate_angle'])
            img.set_array(ri)
        #cbar
        load_cbar(obj,img,ax)

        return img
        
def load_text(text_dict,ax = None):
    
    if type(text_dict) != dict:
        return create_dict_default(text_dict,text_load_list,text_load_list_gui)
    else:
        return load_obj_default(ax.text(1,1,''),text_dict,text_load_list,text_load_list_gui)

def load_label(label_dict,label = None):
    
    if type(label_dict) != dict:
        return create_dict_default(label_dict,label_load_list)
    else:
        return load_obj_default(label,label_dict,label_load_list)

def load_bar(bar_dict,ax = None):
    if type(bar_dict) != dict:
        dic = {'patches':[],'label':bar_dict.get_label()}
        for p in bar_dict.patches:
            dic['patches'].append(create_dict_default(p,patche_load_list))
        return dic
    else:
        patches = bar_dict['patches']
        b2 = ax.bar(np.repeat(1,len(patches)),np.repeat(1,len(patches)))
        for i in range(len(patches)):
            load_obj_default(b2.patches[i],patches[i],patche_load_list)
        if 'label' in bar_dict:
            b2.set_label(bar_dict['label'])
        
        return patches
        

def salva(fig,file = 'graf.plt'):
    dic = load_fig(fig)
    pd.DataFrame({'graf':dic}).to_hdf(file,mode = 'w',key = 'df')

    fig.savefig('.'+file+'_icone.png')
    pasta = tradus_terminal(os.getcwd())
    
    #arrumar icone
    
    os.system('gio set -t string %s/%s metadata::custom-icon file://%s/%s'%\
                              (pasta,file,pasta,'.'+file+'_icone.png'))

def teste_bar():
    fig,ax = plt.subplots()
    b = ax.bar([1,2,3,4,5],[1,4,9,16,25],label = 'asd')
    fb = ax.fill_between([1,2,3,4,5],0,2)

    p = fb.get_paths()[0]
    v = p.vertices
    c = p.codes
    dic = load_fig(fig)
    fig2 = load_fig(dic)
    ax2 = fig2.axes[0]


    fig2.show()

def teste_err():
    fig,ax = plt.subplots()
    Ye = np.random.random((5,4))*2 -1
    x = np.linspace(0,10,4)
    y = np.sin(x)
    line = ax.plot(x,y)[0]
    edown,eup = create_disepertion(Ye)
    shadow_error(line,y+edown,y+eup)
    salva(fig,'teste_err.plt')

def teste_formatter():
    fig,ax = plt.subplots()
    ax.yaxis.set_major_formatter(FuncFormatter("'asd'"))
    fig.show()
    fig2 = load_fig(load_fig(fig))
    fig2.show()
    print(fig2.axes[0].yaxis)
    print(fig2.axes[0].yaxis.get_major_formatter())
#teste_formatter()
#teste_err()
