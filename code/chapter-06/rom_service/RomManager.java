package android.os;

import android.annotation.NonNull;
import android.annotation.Nullable;
import android.compat.annotation.UnsupportedAppUsage;
import android.content.Context;
import android.annotation.SystemService;
import android.os.IRomManager;

@SystemService(Context.ROM_SERVICE)
public final class RomManager {
    private static final String TAG = "RomManager";
    IRomManager mService;
    public RomManager(IRomManager service) {
            mService = service;
    }
    private static RomManager sInstance;
    /**
     *@hide
     */
    @NonNull
    @UnsupportedAppUsage
    public static RomManager getInstance() {
        synchronized (RomManager.class) {
            if (sInstance == null) {

                try {
                    IBinder romBinder = ServiceManager.getServiceOrThrow(Context.ROM_SERVICE);
                    IRomManager romService = IRomManager.Stub.asInterface(romBinder);
                    sInstance= new RomManager(romService);
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