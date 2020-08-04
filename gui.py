# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QApplication, QPushButton, QWidget,
    QToolTip, QDesktopWidget, QMainWindow,
    QAction, qApp, QMenu, QTextEdit, QLabel,
    QHBoxLayout, QVBoxLayout, QFileDialog,
    QComboBox, QSpinBox, QLineEdit, QFrame
)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter
from PyQt5.Qt import Qt
from pathlib import Path
from enigma import (
    enigma, TYPE_I, TYPE_II, TYPE_III, 
    TYPE_IV, TYPE_V, rotor
)
from time import sleep
from string import ascii_letters

location = 'img/keyboard/'


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.enigma = enigma(key='AQL')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.outputline = QTextEdit(self, objectName='outputline')
        self.outputline.setStyleSheet(
            'color: #a3779a; background-color: #444444'
        )
        self.outputline.setAlignment(
            QtCore.Qt.AlignHCenter |
            QtCore.Qt.AlignVCenter
        )

        self.counter = 0
        self.plugboardcounter = 0
        self.plugboardFlag = False

        self.outputline.setReadOnly(True)
        self.lastkeypressed = 'A'
        self.setCentralWidget(QWidget(self))
        self._initUI()


    def _initUI(self) :

        self._menubar_config()
        self._setLayOuts()
        self.setStyleSheet('background-color: #333333')
        self.resize(798, 600)
        self.setWindowTitle('enigma simulator')
        self.show()
        self.setMaximumSize(798, 600)
        self.setMinimumSize(798, 600)
        self.setWindowOpacity(0.95)

    def _setLayOuts(self) :
        mainvbox = QVBoxLayout()
        mainvbox.setObjectName("mainvbox")

        self.rotorselectorhbox = QHBoxLayout()
        self.rotorselectorhbox.setObjectName("rotorselectorhbox")

        monofont = QFont()
        monofont.setFamily("Ubuntu Mono")
        monofont.setPointSize(12)
        monofont.setBold(True)

        self.outputline.setFont(monofont)

        reflectorcbox = QComboBox(self, objectName='reflector')
        reflectorcbox.setFont(monofont)
        reflectorcbox.addItems(['B', 'C'])
        reflectorcbox.setStyleSheet('color: #FFFFFF')
        reflectorcbox.activated[str].connect(
                lambda index, rcbx=reflectorcbox : \
                    self._handle_rotor_change(rcbx, index)
            )
        self.rotorselectorhbox.addStretch(1)
        self.rotorselectorhbox.addWidget(reflectorcbox)

        self.keyselectorhbox = QHBoxLayout(objectName= 'keyselectorhbox')
        self.keyshowalpha = QHBoxLayout(objectName= 'keyshowalpha')
        self.keyselectorhbox.addStretch(1)
        self.keyshowalpha.addStretch(1)

        self.myrotorpos = []

        for r in self.enigma.getrots() :
            self._add_rotor2gui(r)

        self.rotorselectorhbox.addStretch(1)
        plusbotton = QPushButton('+', self, objectName='plusbotton')
        plusbotton.setFont(monofont)
        plusbotton.setStyleSheet(
            '''
            .QPushButton {
                background-color: #333333;
                border-radius: 11px;
                border: 3px solid #777777;
                color: #FFFFFF;
                font-size: 24px;
                font-weight: bold;
                padding: 0px 5px;
            }
            .QPushButton:hover {
                background-color:#777777;
            }
            '''
        )
        plusbotton.clicked.connect(self._handle_rotor_adding)
        self.rotorselectorhbox.insertWidget(len(self.rotorselectorhbox) - 1, plusbotton)
        
        self.keyselectorhbox.addStretch(1)
        self.keyshowalpha.addStretch(1)
        
        keyboardhbox = [
            (QHBoxLayout(), 'qwertyuio'),
            (QHBoxLayout(),  'asdfghjk'),
            (QHBoxLayout(), 'pzxcvbnml')
        ]

        mainvbox.addLayout(self.rotorselectorhbox)
        mainvbox.addLayout(self.keyselectorhbox)
        mainvbox.addLayout(self.keyshowalpha)
        mainvbox.addWidget(self.outputline)

        separator1 = QFrame(self, objectName='separtor1')
        separator1.setFrameShape(QFrame.HLine)
        separator1.setFrameShadow(QFrame.Sunken)
        mainvbox.addWidget(separator1)

        self.my_let_labels = dict()

        for kcb in keyboardhbox :
            for letter in kcb[1] :
                letter_label = QLabel(self, objectName = letter+'_label')
                letter_label.setPixmap(QPixmap(location + letter + '.png'))
                letter_label.setScaledContents(True)
                letter_label.setMaximumSize(60, 60)
                kcb[0].addWidget(letter_label)
                self.my_let_labels[letter.upper()] = letter_label
            
            mainvbox.addLayout(kcb[0])

        separator2 = QFrame(self, objectName= 'separtor2')
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        mainvbox.addWidget(separator2)

        tailhbox = QHBoxLayout()
        tailhbox.addStretch(1)

        copybutton = QPushButton('Copy to clipboard', self, objectName='copybutton')
        copybutton.clicked.connect(self._copy2clipboard)
        copybutton.setFont(monofont)
        copybutton.setStyleSheet(
            '''
            .QPushButton {
                background-color: #333333;
                border-radius: 10px;
                border: 4px solid #777777;
                font-weight: bold;
                color: #ffffff;
                padding: 16px 31px;
            }
            .QPushButton:hover {
                background-color: #777777;
            }
            '''
        )
        tailhbox.addWidget(copybutton)
        tailhbox.addStretch(1)

        plugboardhbox = QHBoxLayout()
        plugboardhbox.addStretch(1)
        
        self.plugboardline = QLineEdit(self, objectName='plugboardline')
        self.plugboardline.setFont(monofont)
        self.plugboardline.setStyleSheet('color: #FFFFFF')
        self.plugboardline.setMaxLength(29)
        plugboardhbox.addWidget(self.plugboardline)
        self.plugboardline.setMinimumSize(260, 30)
        self.plugboardline.setAlignment(
            QtCore.Qt.AlignHCenter |
            QtCore.Qt.AlignVCenter
        )
        self.plugboardline.setReadOnly(True)
        self.plugboardline.keyPressEvent = self._plugboardlinekeypress
        plugboardhbox.addStretch(1)
        mainvbox.addLayout(tailhbox)
        mainvbox.addLayout(plugboardhbox)

        self.centralWidget().setLayout(mainvbox)


    def _plugboardlinekeypress(self, e) :
        try :
            mychr = chr(e.key())

            if mychr in ascii_letters :
                self.plugboardFlag = False

                if not mychr in self.plugboardline.text() :
                    self.plugboardline.setText(
                        self.plugboardline.text() + mychr
                    )
                    self.plugboardcounter = (self.plugboardcounter + 1) % 2

                    if not self.plugboardcounter :
                        self.plugboardline.setText(
                        self.plugboardline.text() + ' '
                    )

                else :
                    sys.stderr.write(
                        'You have chosen that letter already.\n'
                    )
        
        except ValueError :
            if e.key() == Qt.Key_Backspace :
                self.plugboardline.setText(
                    self.plugboardline.text()[:-1]
                )

                self.plugboardcounter = (self.plugboardcounter - 1) % 2

                if not self.plugboardcounter :
                    self.plugboardline.setText(
                        self.plugboardline.text()[:-1]
                    )
            else :
                sys.stderr.write(
                    'Choose valid chars. '
                    'Just ascii suported \n'
                )


    def _menubar_config(self) :
        # MenuBar configuration

        menubar = self.menuBar()
        menubar.setStyleSheet('color: #FFFFFF')

        # File Menu
        fileMenu = menubar.addMenu('&File')

        newAct = QAction(QIcon('img/new_white.png'),'&New', self)
        newAct.setStatusTip('Create new file')

        impMenu = QMenu('Import...', self)
        impMenu.setStyleSheet('color: #FFFFFF')
        impfileAct = QAction('Import file', self)
        impfileAct.setStatusTip('Import a file')
        impfileAct.triggered.connect(self._showImportDialog)
        impMenu.addAction(impfileAct)

        exitAct = QAction(QIcon('img/exit_white.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)
        
        fileMenu.addAction(newAct)
        fileMenu.addMenu(impMenu)
        fileMenu.addAction(exitAct)

        # View Menu
        viewMenu = menubar.addMenu('&View')

        viewStatAct = QAction('Status bar', self, checkable=True)
        viewStatAct.setStatusTip('Show/Hide status bar')
        viewStatAct.setChecked(True)
        viewStatAct.triggered.connect(self._toggleMenu)

        viewToolBarAct = QAction('Tool bar', self, checkable=True)
        viewToolBarAct.setStatusTip('Show/Hide tool bar')
        viewToolBarAct.setChecked(False)
        viewToolBarAct.triggered.connect(self._toggleBar)

        viewMenu.addAction(viewStatAct)
        viewMenu.addAction(viewToolBarAct)


        # Tool bar
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAct)
        self.toolbar.hide()

        self.statusBar().setStyleSheet('color: #FFFFFF')


    def _showImportDialog(self) :
        homedir = str(Path.home())
        filename = QFileDialog.getOpenFileName(self, 'Import file', homedir)

        print(filename)

        if filename[0] :
            file_handle = open(filename[0], 'r')
            data = file_handle.read()
            cripto = self.enigma.run(data)
            self.outputline.setText(cripto)


    def _toggleMenu(self, state) :
        if state :
            self.statusBar().show()
        else :
            self.statusBar().hide()


    def _toggleBar(self, state) :
        if state :
            self.toolbar.show()
        else :
            self.toolbar.hide()


    def _handle_rotor_change(self, rcbx, newtype) :
        if rcbx.objectName() == 'reflector' :
            self.enigma.set_reflector(newtype)
        
        else :
            index = self.rotorselectorhbox.indexOf(rcbx) - 2
            myrots = self.enigma.getrots()
            
            if newtype == 'I':
                myrots[index]._set_config(name=newtype, config=TYPE_I)
            elif newtype == 'II':
                myrots[index]._set_config(name=newtype, config=TYPE_II)
            elif newtype == 'III':
                myrots[index]._set_config(name=newtype, config=TYPE_III)
            elif newtype == 'IV':
                myrots[index]._set_config(name=newtype, config=TYPE_IV)
            elif newtype == 'V':
                myrots[index]._set_config(name=newtype, config=TYPE_V)


    def _handle_key_spin(self, ksx, pos) :
        index = self.keyselectorhbox.indexOf(ksx) - 1
        myrots = self.enigma.getrots()
        myrots[index].set_pos(pos)
        self.myrotorpos[index][2].setText(ascii_letters.upper()[pos])


    def _create_rotor_gui_components(self, r) :
        monofont = QFont()
        monofont.setFamily("Ubuntu Mono")
        monofont.setPointSize(12)
        monofont.setBold(True)

        myrotcbox = QComboBox(self)
        myrotcbox.addItems(['I', 'II', 'III', 'IV', 'V'])
        myrotcbox.setStyleSheet('color: #FFFFFF')
        myrotcbox.setFont(monofont)
        myrotcbox.setCurrentText(r.name)
        myrotcbox.activated[str].connect(
            lambda index,cbox=myrotcbox : \
                self._handle_rotor_change(cbox, index)
        )

        mykeysbox = QSpinBox(self)
        mykeysbox.setStyleSheet('color: #FFFFFF')
        mykeysbox.setFont(monofont)
        mykeysbox.setAlignment(QtCore.Qt.AlignCenter)
        mykeysbox.setMaximum(25)
        mykeysbox.setValue(r.getpos())
        mykeysbox.setWrapping(True)
        mykeysbox.valueChanged.connect(
            lambda index, kbx=mykeysbox: \
                self._handle_key_spin(kbx, index)
        )

        mykeybutton = QPushButton(
            ascii_letters.upper()[r.getpos()],
            self
        )
        mykeybutton.setFont(monofont)
        mykeybutton.setStyleSheet(
            '''
            .QPushButton {
                background-color: #333333;
                border-radius: 5px;
                border: 2px solid #777777;
                font-weight: bold;
                color: #ffffff;
                padding: 6px 9px;
            }
            .QPushButton:hover {
                background-color: #770000;
            }
            '''
        )
        mykeybutton.clicked.connect(
            lambda index, kbtn=mykeybutton : \
                self._handle_rotor_remove(kbtn, index)
        )

        return myrotcbox, mykeysbox, mykeybutton


    def _add_rotor2gui(self, r)  :
        (
            myrotcbox, 
            mykeysbox, 
            mykeybutton
        ) = self._create_rotor_gui_components(r)
        
        self.rotorselectorhbox.addWidget(myrotcbox)      
        self.keyselectorhbox.addWidget(mykeysbox)
        self.keyshowalpha.addWidget(mykeybutton)
        
        self.myrotorpos.append((myrotcbox, mykeysbox, mykeybutton))


    def _handle_rotor_adding(self) :
        newrot = self.enigma._addrotor(rotor())

        if newrot != None :
            index = len(self.rotorselectorhbox) - 2

            (
                myrotcbox, 
                mykeysbox, 
                mykeybutton
            ) = self._create_rotor_gui_components(newrot)
            
            self.rotorselectorhbox.insertWidget(index, myrotcbox)
            index = len(self.keyselectorhbox) - 1
            self.keyselectorhbox.insertWidget(index, mykeysbox)
            self.keyshowalpha.insertWidget(index, mykeybutton)
            self.myrotorpos.append((myrotcbox , mykeysbox, mykeybutton))

        
    def _handle_rotor_remove(self, kbtn, val) :
        index = self.keyshowalpha.indexOf(kbtn) - 1 # remember the Stretch

        if not self.enigma._remove_rotor(index) :
            childcombo = self.myrotorpos[index][0]
            self.rotorselectorhbox.removeWidget(childcombo)
            childcombo.deleteLater()

            childspinbox = self.myrotorpos[index][1]
            self.keyselectorhbox.removeWidget(childspinbox)
            childspinbox.deleteLater()
            
            self.keyshowalpha.removeWidget(kbtn)
            kbtn.deleteLater()

            self.myrotorpos.remove(self.myrotorpos[index])


    def keyPressEvent(self, e) :
        try :
            if chr(e.key()) in ascii_letters :
                if not self.plugboardFlag :
                    self.enigma._set_plugboard(
                        self.plugboardline.text().strip().split(' ')
                    )
                self.my_let_labels[self.lastkeypressed].setPixmap(
                    QPixmap(location + self.lastkeypressed.lower() + '.png')
                )

                outkey = self.enigma.step(chr(e.key()))
                self.my_let_labels[outkey].setPixmap(
                    QPixmap(location + outkey.lower() + '_h.png')
                )

                rotors = self.enigma.getrots()

                for posPbutton, rot in zip(self.myrotorpos, rotors) :
                    posPbutton[1].setValue(rot.getpos())
                    posPbutton[2].setText(ascii_letters.upper()[rot.getpos()])

                self.outputline.setText(self.outputline.toPlainText() + outkey)
                self.counter = (self.counter + 1) % 5

                if not self.counter :
                    self.outputline.setText(self.outputline.toPlainText() + ' ')
                
                self.lastkeypressed = outkey
        except ValueError :
            if e.key() == Qt.Key_Backspace :
                self.counter = (self.counter - 1) % 5
                self.outputline.setText(self.outputline.toPlainText()[:-1])

                if not self.counter :
                    self.outputline.setText(self.outputline.toPlainText()[:-1])
                
            else :
                sys.stderr.write('Write just valid chars.\n')
    
    def _copy2clipboard(self) :
        QApplication.clipboard().setText(self.outputline.toPlainText())


def main() :
    app = QApplication(sys.argv)
    w = MyApp() 
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()