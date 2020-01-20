import maya.mel as mel
import maya.cmds as cmds

density = 0.25
radius = 4
sections = 6
smooth = 0
taper = 0

def selection():
	return cmds.ls(sl=1, fl=1)


def make_tube(radius, unit, density, sections, fills):
	units = {'mm' : 0.001, 'cm' : 0.01, 'dcm' : 0.1, 'm' : 1}
	new_curve = None
	is_edge = cmds.filterExpand(sm=32)
	if is_edge:
		new_curve = make_curve()

	sel_curves = cmds.ls(sl=1, fl=1)
	for c in sel_curves:
		cmds.select(c)
		tube_name = c+'Tube'
		mel.eval(' AttachBrushToCurves; convertCurvesToStrokes; ')
		temp_stroke = cmds.ls(sl=1,fl=1)
		st_shape = cmds.listRelatives(temp_stroke)[0]
		edit_density(density, st_shape)
		mel.eval('global string $mel_brush; $mel_brush=doPaintEffectsToPoly(1,0,1,1,100000);')
		brush = cmds.ls(sl=1,fl=1)[0].split('MainShape')[0]
		edit_radius(radius, unit, brush)
		edit_sections(sections, brush)
		cmds.sets(forceElement='initialShadingGroup',e=1)
		print tube_name, temp_stroke, new_curve, brush, st_shape
		try:
			pass
			# cmds.parent(w=1)
		except Exception as e:
			pass

		transform = cmds.ls(sl=1,fl=1)[0]
		# cmds.delete(transform.split('Main')[0] + 'MeshGroup')
		if fills:
			caps = make_fills(brush)
		else:
			caps = None
		cmds.select(transform)
		#create taper points
		cmds.setAttr("{}.pressureScale[0].pressureScale_Position".format(st_shape), 0)
		cmds.setAttr("{}.pressureScale[1].pressureScale_Position".format(st_shape), 1)
		cmds.setAttr("{}.pressureScale[0].pressureScale_FloatValue".format(st_shape), 1)
		cmds.setAttr("{}.pressureScale[1].pressureScale_FloatValue".format(st_shape), 1)
		cmds.setAttr("{}.pressureScale[1].pressureScale_Interp".format(st_shape), 1)
		return dict( ( 
					   ('tube_name',tube_name),
					   ('transform',transform),
					   ('temp_stroke',temp_stroke),
					   ('new_curve', new_curve),
					   ('brush', brush),
					   ('st_shape', st_shape),
					   ('caps', caps)
					) )

		
def clean(tube_name, transform, temp_stroke, new_curve, caps):
	cmds.polyMultiLayoutUV( scale=1, rotateForBestFit=2, layout=2 )
	cmds.delete(transform, ch=1)
	cmds.delete(temp_stroke)
	if new_curve:
		cmds.delete(new_curve)
	cmds.rename(transform, tube_name)
	if caps:
		try:
			[ mel.eval (' select -r {}; performNormalBasedProjection 0; '.format(i)) for i in caps ]
		except:
			pass


def make_fills(brush):
	cmds.setAttr( brush +'.endCaps', 1 )
	# print 'DelayCAP'
	# all_faces = cmds.ls (cmds.polyListComponentConversion(transform, tf=1, bo=1), fl=1)
	# border_edges = cmds.ls (cmds.polyListComponentConversion(all_faces, te=1, bo=1), fl=1)
	# print 'border edges...',border_edges
	# cmds.polyCloseBorder(border_edges, ch=1)
	# caps = cmds.ls(cmds.polyListComponentConversion(border_edges, tf=1, internal=1), fl=1)
	# print 'CAPS>>>', caps
	# return caps


def edit_radius(radius, unit, brush):
	units = {'mm' : 0.001, 'cm' : 0.01, 'dcm' : 0.1, 'm' : 1}
	cmds.setAttr("{}.brushWidth".format(brush), radius*units[unit])


def edit_density(density, st_shape):
	cmds.setAttr("{}.sampleDensity".format(st_shape), density)


def edit_sections(sections, brush):
	cmds.setAttr("{}.tubeSections".format(brush), sections)


def edit_smooth(value, st_shape):
	cmds.setAttr("{}.smoothing".format(st_shape), value)

def edit_taper(value, st_shape):
	print 'taper_slider>>', value
	taper = 1-(abs(value)/5)*0.1
	print taper
	if value < 0:
		position = 0
	else:
		position =1

	cmds.setAttr("{}.pressureScale[{}].pressureScale_FloatValue".format(st_shape, position), taper)

def num_spans(curve):
	numSpans = cmds.getAttr(curve+'.spans')
	degree = cmds.getAttr(curve+'.degree')
	form = cmds.getAttr(curve+'.form')
	numCVs = numSpans + degree
	if ( form == 2 ):
	 	numCVs -= degree
 	return numCVs


def kill_caps(brush):
	cmds.setAttr( brush +'.endCaps', 0 )
	return None


def select(obj):
	cmds.select(obj)


def make_curve():
	new_curve = cmds.polyToCurve(degree=1, form=2, conformToSmoothMeshPreview=1)[0]
	spans =  num_spans(new_curve) *2
	cmds.rebuildCurve(new_curve, rt=0, ch=1, end=1, d=3, kr=2, s=spans, kcp=0, tol=0.01, kt=0, rpo=1, kep=1)
	first_cv = new_curve + '.cv[0]'
	cmds.move(0.0001, 0.0001, 0.0001, first_cv ,r=True, )
	return new_curve



def make_tube_b(radius, unit, density, sections, fills):
	units = {'mm' : 0.001, 'cm' : 0.01, 'dcm' : 0.1, 'm' : 1}
	new_curve = None
	is_edge = cmds.filterExpand(sm=32)
	if is_edge:
		new_curve = make_curve()

	circle(c=(0, 0, 0), ch=1, d=3, ut=0, sw=360, s=8, r=1, tol=0.01, nr=(0, 1, 0))


def make_set(items):
	new_set =  cmds.sets( items )
	return cmds.sets(e=1, fl=new_set )

def set_to_sel( m_set ):
	return sorted(cmds.ls(cmds.sets( m_set, q=1 ),fl=1))