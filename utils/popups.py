from pyqttoast import Toast, ToastPreset, ToastPosition


def defaultErrorToast(self):
    toast = Toast(self)
    toast.setDuration(1000)
    toast.setTitle('Error')
    toast.setText('INCORRECT FORMAT')
    toast.setPosition(ToastPosition.CENTER)
    toast.applyPreset(ToastPreset.ERROR)
    toast.show()