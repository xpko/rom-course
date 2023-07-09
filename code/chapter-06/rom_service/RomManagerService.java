package com.android.server;

import android.os.RemoteException;
import android.os.IRomManager;

public class RomManagerService extends IRomManager.Stub {

    private String TAG="RomManagerService";
    @Override
    public String hello()  throws RemoteException{
        return "hello rom service";
    }
}