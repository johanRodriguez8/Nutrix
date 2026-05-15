from pyqttoast import Toast, ToastPreset, ToastPosition


def defaultErrorToast(self,error:str):
    toast = Toast(self)
    toast.setDuration(1000)
    toast.setTitle('Error')
    toast.setText(f'{error}')
    toast.setPosition(ToastPosition.CENTER)
    toast.applyPreset(ToastPreset.ERROR)
    toast.show()