/******************************************************************************
 * 
 *  GMonE: A customizable monitoring tool for distributed systems
 *  Copyright (C) 2010  Jesus Montes
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *  
 *****************************************************************************/

package common;
import java.rmi.Remote;
import java.rmi.RemoteException;
import java.util.*;

public interface GMonEAccessInterface extends Remote {
	
    //public Vector getConfiguration() throws RemoteException;
    
    public Vector<String> getParams() throws RemoteException;
    
    public Vector<String> getHosts() throws RemoteException;

    public Vector<GValue> query(String sParam, String sHost, long lIni, long lEnd, String sClient) throws RemoteException;

    public Vector<GValue> query(String sParam, String sHost, long lIni, long lEnd) throws RemoteException;

    public Vector<GValue> query(String sParam, long lIni, long lEnd) throws RemoteException;

    public Vector<GValue> queryLast(String sParam, long lTime) throws RemoteException;
    
    public Vector<GValue> queryGlobal(String sParam, long lTime) throws RemoteException;

    public void setPeriod(int tiempo) throws RemoteException;
  
    //public void startService() throws RemoteException;
    
}
