import maya.cmds as cmds
from PySide2 import QtCore, QtGui, QtWidgets
from maya import OpenMayaUI as omui
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from shiboken2 import wrapInstance
import custom_title_bar2 as tb
import mario_UI as ui
import mario_mel as engine
#-----------------------------------------------Enable those two for editing
reload(engine)
reload(ui)
reload(tb)

# --------------------------------------------------- High DPI monitors adaptation
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
	QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
 
if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
	QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
# --------------------------------------------------- Get Maya main window
def maya_main_window():
		main_window_ptr = omui.MQtUtil.mainWindow()
		return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class MyBar(tb.MyBar):
	def __init__(self, parent=None, *args, **kwargs):
		super(MyBar, self).__init__(parent)

		self.layout.setContentsMargins(4,4,4,4)
		self.btn_close.setParent(None)
		self.title.deleteLater()
		self.title = QtWidgets.QLabel("MARIO")
		font = QtGui.QFont()
		font.setFamily("Segoe UI")
		font.setPointSize(10)
		font.setWeight(75)
		font.setBold(True)
		self.title.setStyleSheet("QWidget { font: bold 12px;color:rgba(179,206,254);}")
		self.title.setFont(font)
		self.title.setFixedHeight(15)
		self.title.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
		self.layout.addWidget(self.title)
		self.layout.addWidget(self.btn_close, alignment=QtCore.Qt.AlignTop)
		self.custom_button(self.btn_close)

	def custom_button(self, button):
		btn_size = 15
		btn_color = 'rgba(179,206,254)'
		self.bg_color = self.palette().color(QtGui.QPalette.Background).name()
		button.setStyleSheet('''QPushButton {
											border: 1px solid  %s ;
											color: %s ;
											border-radius: 0px;
											background-color:  %s;
											}

								QPushButton:pressed {
											color: 'white' ;
											background-color: %s;

											}
								QPushButton:hover:!pressed {
											color: %s;
											background-color: %s;

											}
										'''
										%(btn_color,btn_color, self.bg_color, btn_color, self.bg_color, btn_color)
										)

		self.btn_close.setFixedSize(btn_size,btn_size)


#-----------------------------------------------------------------UI setup
class Mario_main(ui.Ui_Mario, QtWidgets.QWidget):


	def __init__(self,  *args, **kwargs):
		super(Mario_main, self).__init__( *args, **kwargs)

		
		#-------------------------------------------------Create settings
		self.settings = QtCore.QSettings('PixelEmbargo','Mario')
		geometry = self.settings.value('geometry', '')
		self.restoreGeometry(geometry)
		self.tlayout = QtWidgets.QVBoxLayout()
		self.title_bar = MyBar(self)
		self.tlayout.addWidget(self.title_bar)
		self.setLayout(self.tlayout)
		self.tlayout.setContentsMargins(0,0,0,0)
		self.tlayout.setObjectName('Main_l')
		self.tlayout.addStretch(-1)
		self.setMinimumSize(180, 270)
		# self.setWindowFlags(QtCore.Qt.Tool) 
		self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint)
		# self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.pressing = False
		self.setupUi(self)


	#--------------------------------------------------------Customize UI
	def setupUi (self, Sets):
		super(self.__class__, self).setupUi(Sets)
			
		self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		self.setWindowTitle('Mario')
		self.tlayout.addLayout(self.verticalLayout_2)

		#----------------------------Customize lineEdits
		self.bg_color = self.palette().color(QtGui.QPalette.Background).name()
		self.line_edits = [self.rad_line, 
						   self.dencity_line,
						   self.sections_line,
						   self.smooth_line,
						   self.taper_line
						  ]
		[self.line_setup(i, self.bg_color) for i in self.line_edits]

		#--------------------------- Customize sliders
		self.sliders = [ 'radius', 'density', 'sections', 'smooth', 'taper'  ]
		[self.custom_slider(i) for i in self.sliders]

		self.rad_sl.setRange(1,20)
		self.dencity_sl.setRange(1, 40)
		self.sections_sl.setRange(3,12)
		self.smooth_sl.setRange(0,50)
		self.taper_sl.setRange(-50,50)
		# connect edit lines to sliders
		self.rad_sl.valueChanged.connect(lambda: self.change_line(self.rad_sl, self.rad_line))
		self.dencity_sl.valueChanged.connect(lambda: self.change_line(self.dencity_sl, self.dencity_line))
		self.sections_sl.valueChanged.connect(lambda: self.change_line(self.sections_sl, self.sections_line))
		self.smooth_sl.valueChanged.connect(lambda: self.change_line(self.smooth_sl, self.smooth_line))
		self.taper_sl.valueChanged.connect(lambda: self.change_line(self.taper_sl, self.taper_line))

		# self.rad_sl.sliderReleased.connect(self.caps_refresh)
		self.dencity_sl.sliderReleased.connect(self.caps_refresh)
		self.sections_sl.sliderReleased.connect(self.caps_refresh)
		# self.dencity_sl.sliderPressed.connect(self.caps_kill)
		# self.sections_sl.sliderPressed.connect(self.caps_kill)

		self.rad_line.editingFinished.connect(lambda: self.change_slider(self.rad_sl, self.rad_line))
		self.dencity_line.editingFinished.connect(lambda: self.change_slider(self.dencity_sl, self.dencity_line))
		self.sections_line.editingFinished.connect(lambda: self.change_slider(self.sections_sl, self.sections_line))
		self.smooth_line.editingFinished.connect(lambda: self.change_slider(self.smooth_sl, self.smooth_line))
		self.taper_line.editingFinished.connect(lambda: self.change_slider(self.taper_sl, self.taper_line))
		# change font size if line is too long
		self.rad_line.textChanged.connect(lambda: self.change_font(self.rad_line))
		self.dencity_line.textChanged.connect(lambda: self.change_font(self.dencity_line))
		self.sections_line .textChanged.connect(lambda: self.change_font(self.sections_line ))

		#connect radio buttons
		radiobuttons = [ self.mm_b, self.cm_b, self.dcm_b, self.m_b ]
		[i.toggled.connect(self.radio_mode) for i in radiobuttons]


		#customize buttons
		self.custom_button(self.create_b)
		self.custom_button(self.finalize_b)
		#customize checkboxes
		[ self.custom_checkbox(i) for i in (self.caps_cb, self.dynamic_cb) ]
		#buttons functions
		self.create_b.released.connect(self.make_tube)
		self.finalize_b.released.connect(self.finalize_tube)
		# action on chckbox click
		self.caps_cb.clicked.connect(self.make_caps)
		#hide the button from UI
		self.dynamic_cb.setParent(None)




		self.set_defaults()



	def line_setup(self, w, bg_color):
		self.rad_lo.setAlignment(QtCore.Qt.AlignVCenter)
		p = w.palette()
		p.setColor(w.backgroundRole(), bg_color)
		w.setPalette(p)
		w.setFrame(False)
		w.setReadOnly(False)
		w.setFixedHeight(23)
		f = w.font()
		f.setPointSize(11)
		w.setFont(f)
		w.setAlignment( QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight )
		w.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
		

	def set_defaults(self):
		self.edit_mode = False
		self.rad_line.setText(str(engine.radius))
		self.dencity_line.setText(str(engine.density))
		self.sections_line.setText(str(engine.sections))
		self.smooth_line.setText(str(engine.smooth))
		self.taper_line.setText(str(engine.taper))
		self.cm_b.setChecked(True)
		self.caps_cb.setChecked(False)
		#----------------------initial slider positions
		self.rad_sl.setSliderPosition(int(self.rad_line.text()))
		self.dencity_sl.setSliderPosition(float(self.dencity_line.text())*20)
		self.sections_sl.setSliderPosition(int(self.sections_line.text()))
		#---------------------greyout buttons
		self.dynamic_cb.setEnabled(False)
		self.finalize_b.setEnabled(False)


	#-------------------------------------------------------------------------------------UI methods
	
	def change_line(self, slider, line):
		curr_slider = slider.value()
		if slider ==  self.dencity_sl:
			curr_slider = float(slider.value())/20
		line.setText(str(curr_slider))
		[ l.clearFocus() for l in self.line_edits ]
		if self.edit_mode:
			self.edit_tube(slider)


	def change_slider(self, slider, line):
		curr_line = float(line.text())
		if slider == self.dencity_sl:
			curr_line *= 20
		slider.blockSignals(True)
		slider.setSliderPosition(curr_line)
		slider.blockSignals(False)
		[ l.clearFocus() for l in self.line_edits ]
		if self.edit_mode:
			self.edit_tube(slider)


	def radio_mode(self):
		radioButton = self.sender()
		if radioButton.isChecked():
			self.unit = radioButton.objectName().split('_')[0]
		if self.edit_mode:
			self.edit_tube(self.rad_sl)


	def change_font(self, qline):
		print qline.text()
		if len(qline.text()) > 4:
			qline.setFixedHeight(20)
			f = qline.font()
			f.setPointSize(10)
		else:
			qline.setFixedHeight(23)
			f = qline.font()
			f.setPointSize(11)
		qline.setFont(f)



	def blendColors(self, first, second, ratio=0.5, alpha=100):
		ratio2 = 1 - ratio
		return QtGui.QColor(
			(first.red() * ratio) + (second.red() * ratio2),
			(first.green() * ratio) + (second.green() * ratio2),
			(first.blue() * ratio) + (second.blue() * ratio2),
			alpha,
			)


	def custom_slider(self, slider):
		palette = { 
					'radius': {'rgb(255, 130, 250)': (self.rad_sl, self.rad_line, self.rad_l, self.mm_b, self.cm_b, self.dcm_b, self.m_b)},
				   'density': {'rgb(138, 170, 255)': (self.dencity_sl, self.dencity_line, self.dencity_l)},
				  'sections': {'rgb(138, 170, 255)': (self.sections_sl, self.sections_line, self.sections_l)},
				    'smooth': {'rgb(138, 170, 255)': (self.smooth_sl, self.smooth_line, self.smooth_l)},
				     'taper': {'rgb(138, 170, 255)': (self.taper_sl, self.taper_line, self.taper_l)}
				  }
		sl_color = palette[slider].keys()[0]
		sl = palette[slider][sl_color][0]
		line =  palette[slider][sl_color][1]
		lbl = palette[slider][sl_color][2]
		radios = palette[slider][sl_color][3:]

		sl.setStyleSheet('''QSlider::groove:horizontal 
														{ border: 0px solid #999999; 
														  height: 1px;
														  Background : %s;
														  margin: 2px 0;
														  }
								QSlider::handle:horizontal
														 {
														 background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 , stop:1 #8f8f8f);
														 border: 1px solid %s;
														 width: 18px;
														 margin: -2px 0; /* handle is placed by default on the contents rect of the groove. Expand outside the groove */
														 border-radius: 3px;
														}'''
														%(sl_color, sl_color)
							)

		line.setStyleSheet('''color: {}; BAckground: {}'''.format(sl_color, self.bg_color))
		lbl.setStyleSheet('''color: {}; BAckground: {}'''.format(sl_color, self.bg_color))
		for r in radios:
			r.setStyleSheet('''color: {}; BAckground: {}'''.format(sl_color, self.bg_color))


	def custom_button(self, button):
		b_palette = {
					  self.create_b : (36,146,255),
					self.finalize_b : (36,146,255)
				  }

		bg_color = self.palette().color(QtGui.QPalette.Background)
		fg_color = QtGui.QColor(*(b_palette[button]))
		white_color = QtGui.QColor('white')
		over_color = self.blendColors(fg_color, bg_color , ratio=0.5, alpha=100).name()
		text_color = self.blendColors(fg_color, white_color , ratio=0.5, alpha=100).name()
		bright_text = self.blendColors(fg_color, white_color , ratio=0.3, alpha=100).name()
		pressed_color = self.blendColors(fg_color, bg_color , ratio=0.2, alpha=100).name()
		hover_color = self.blendColors(bg_color, fg_color , ratio=0.5, alpha=100).name()

		new_gradient = ''' qlineargradient(spread:reflect, x1:0.523, y1:1, x2:0.557, y2:0, stop:0 rgba(23, 34, 46, 255), 
											stop:0.6875 rgba(35, 46, 56, 255), stop:1 rgba(54, 67, 81, 255)) '''

		button.setStyleSheet('''QPushButton {
									border: 0.5px solid  %s ;
									color: %s ;
									border-radius: 0px;
									background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 %s, stop: 1 %s);
									min-width: 80px;
								}

							QPushButton:pressed {
									color: 'white' ;
									background-color: %s;

							}
							QPushButton:hover:!pressed {
									color: %s ;
									background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 %s, stop: 1 %s);

							}
							QPushButton:disabled {
									color: 'grey' ;
									border: 0.5px solid  'grey' ;

							}
										'''
							%(over_color, text_color, bg_color, bg_color, pressed_color, bright_text, hover_color, hover_color )
										)
		button.setMinimumSize(QtCore.QSize(50,20))


	def custom_checkbox(self, checkbox):
		cb_color = 'rgba(179,206,254)'
		checkbox.setStyleSheet('''QCheckBox {
											color: %s ;
										}
								 QCheckBox:disabled {
											color: 'grey' ;
										}
										'''
										%(cb_color)
										)

	#------------------------------------Functional methods

	def make_tube(self):
		self.sel = engine.selection()
		self.radius =  float(self.rad_line.text())
		self.density = float(self.dencity_line.text())
		self.sections = float(self.sections_line.text())
		self.smooth = float(self.smooth_line.text())
		self.taper = float(self.taper_line.text())
		self.fill = self.caps_cb.isChecked()
		pars = engine.make_tube(self.radius, self.unit, self.density, self.sections, self.fill)
		self.tube_name = pars['tube_name']
		self.transform = pars['transform']
		self.temp_stroke = pars['temp_stroke']
		self.new_curve = pars['new_curve']
		self.brush = pars['brush']
		self.st_shape = pars['st_shape']
		self.caps = pars['caps']
		# enable button
		self.finalize_b.setEnabled(True)
		# edit_mode
		self.edit_mode = True


	def finalize_tube(self):
		try:
			engine.clean(self.tube_name, self.transform, self.temp_stroke, self.new_curve, self.caps)
		except Exception as e:
			print e

		self.tube_name, self.transform, self.temp_stroke, self.new_curve = [None]*4
		self.edit_mode = False


	def edit_tube(self, slider):
		if slider == self.rad_sl:
			self.radius =  float(self.rad_line.text())
			engine.edit_radius(self.radius, self.unit, self.brush)
		if slider == self.dencity_sl:
			self.density =  float(self.dencity_line.text())
			engine.edit_density(self.density, self.st_shape)
		if slider == self.sections_sl:
			self.sections = int(self.sections_line.text())
			engine.edit_sections(self.sections, self.brush)
		if slider == self.smooth_sl:
			self.smooth = float(self.smooth_line.text())
			engine.edit_smooth(self.smooth, self.st_shape)
		if slider == self.taper_sl:
			self.taper = float(self.taper_line.text())
			engine.edit_taper(self.taper, self.st_shape)


	def caps_refresh(self):
		if self.edit_mode:
			if self.caps:
				self.caps = engine.make_fills(self.brush)
				engine.select(self.brush)



	def caps_kill(self):
		if self.edit_mode:
			self.caps = engine.kill_caps(self.brush)


	def make_caps(self):
		if self.edit_mode:
			if self.caps_cb.isChecked():
				self.caps = engine.make_fills(self.brush)
				print 'caps>>>', self.caps
			else:
				self.caps = engine.kill_caps(self.brush)




#------------------------------------------------------Window Position control
	def closeEvent(self,event):
		geometry = self.saveGeometry()
		self.settings.setValue('geometry', geometry)       #save window position
		Mario_window.setParent(None)
		Mario_window.deleteLater()
		print ('Mario Closed')



def show():
	#---------------------------------------------------Close UI window if exists
	global Mario_window
	try:
		Mario_window.close()
	except:
		pass

	Mario_window = Mario_main(parent=maya_main_window())
	Mario_window.show()                  #open window


show()