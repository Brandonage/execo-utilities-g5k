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

import java.rmi.*;
import java.util.Vector;

public interface GMonEMonInterface extends Remote {
	
    public void insertParam (String function, String parameter, String [] list) throws RemoteException;
    
    public void changeParam (String parameter, String function) throws RemoteException;

    public Vector<String> getParamList() throws RemoteException;

    public Vector<GValue> consult (String parameter) throws RemoteException;
	
    public Vector<GValue> consult (String parameter, String function) throws RemoteException;

    // --------------------------------------------------------
    // Publisher operations

    public void setPeriod(int period) throws RemoteException;
    public int getPeriod() throws RemoteException;
    
    public void setSubscriberURL(String subscriber) throws RemoteException;
    public String getSubscriberURL() throws RemoteException;
    public Vector<String> getSubscriberURLs() throws RemoteException;

    public void publishParam(String param, String function) throws RemoteException;
    public Vector<GHost> getPublishedParams() throws RemoteException;

    public void startPublisher() throws RemoteException;

}
