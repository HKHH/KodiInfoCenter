import xbmc
import xbmcaddon

# Hole die Instanz des aktuellen Addons
addon = xbmcaddon.Addon()
systimeformat = addon.getSetting("systimeformat")

# Falls LOGNOTICE nicht existiert, verwende LOGINFO als Fallback
log_level = xbmc.LOGNOTICE if hasattr(xbmc, 'LOGNOTICE') else xbmc.LOGINFO

xbmc.log("systimeformat_HKL: " + systimeformat, log_level)
