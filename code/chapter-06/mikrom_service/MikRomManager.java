package android.os;

import android.annotation.NonNull;
import android.annotation.Nullable;
import android.compat.annotation.UnsupportedAppUsage;
import android.content.Context;
import android.annotation.SystemService;
import android.os.IMikRomManager;

@SystemService(Context.MIKROM_SERVICE)
public final class MikRomManager {
    private static final String TAG = "MikRomManager";
    IMikRomManager mService;
    public MikRomManager(IMikRomManager service) {
            mService = service;
    }
    private static MikRomManager sInstance;
    /**
     *@hide
     */
    @NonNull
    @UnsupportedAppUsage
    public static MikRomManager getInstance() {
        synchronized (MikRomManager.class) {
            if (sInstance == null) {

                try {
                    IBinder mikromBinder = ServiceManager.getServiceOrThrow(Context.MIKROM_SERVICE);
                    IMikRomManager mikromService = IMikRomManager.Stub.asInterface(mikromBinder);
                    sInstance= new MikRomManager(mikromService);
                } catch (ServiceManager.ServiceNotFoundException e) {
                    throw new IllegalStateException(e);
                }
            }
            return sInstance;
        }
    }
    @Nullable
    public String hello(){
        try{
            return mService.hello();
        }catch (RemoteException ex){
            throw ex.rethrowFromSystemServer();
        }
    }
}