package com.android.server;

import android.os.RemoteException;
import android.os.IMikRomManager;

public class MikRomManagerService extends IMikRomManager.Stub {

    private String TAG="MikRomManagerService";
    @Override
    public String hello()  throws RemoteException{
        return "hello mikrom service";
    }
}