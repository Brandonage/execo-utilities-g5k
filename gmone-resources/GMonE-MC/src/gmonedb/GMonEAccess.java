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

package gmonedb;

import java.rmi.*;
import java.rmi.server.*;
import java.io.*;
import java.util.*;

import common.*;

public class GMonEAccess extends UnicastRemoteObject implements GMonEAccessInterface, Serializable {

	private static final long serialVersionUID = 1L;
	private int period = 60; // Periodo de muestreo
	private DBAccessInterface bd; // Objeto de acceso a la base de datos
	String ssHost = "localhost";
	GMonET tProg; // thread to execute the main loop of the monitoring service

	//boolean subscriber = false;
	String[] subscriptions = null;

	UpdaterTMC updater = null;
	SubscriberTMC sub = null;
	
	// ----------------------------------------------------------------------------------------------
	/*
	public GMonEAccess () throws RemoteException {

		GMonELogger.message("Creating GMonEAccess... (1)");
		bd = (DBAccessInterface) new DBAccessSQL("org.sqlite.JDBC", "jdbc:sqlite:"+ficheroBD);
		//bd = (DBAccessInterface) new DBAccessCassandra();

	}*/

	public GMonEAccess (String host, DBAccessInterface dbAccess) throws RemoteException {

		ssHost = host;
		bd = dbAccess;
	}

	// ----------------------------------------------------------------------------------------------
	public Vector<String> getParams() throws RemoteException {
		
		return bd.readParams();
	}

	// ----------------------------------------------------------------------------------------------
	public Vector<String> getHosts() throws RemoteException {

		return bd.readHosts();
	}

	// ----------------------------------------------------------------------------------------------
	public void setPeriod(int time) throws RemoteException {

		period = time;
	}
	// ----------------------------------------------------------------------------------------------
	public int getPeriod() {

		return period;
	}	

	// ----------------------------------------------------------------------------------------------
	public Vector<String> getConfiguration(){

		return null;
	}

	// ----------------------------------------------------------------------------------------------	
	public void startService ()  {

		updater = new UpdaterTMC(this, ssHost);
		updater.init();
		sub = new SubscriberTMC(this, bd);
		sub.setPeriod(period);
		sub.start();
	}

	// ----------------------------------------------------------------------------------------------
	//
	// The "query" function allows the user to ask the system for monitored values. The method
	// parameters have the following semantic:
	//
	//    sParam  - The parameter name
	//
	//    sHost   - The host name
	//
	//    lIni    - The initial query time. It can have the following values:
	//
	//                - A greater than zero value (>0): Represents a absolute UNIX time, in 
	//                                                  milliseconds (i.e. 1164368881325).
	//                - A lesser than zero value (<0) : A UNIX time, relative to the actual time
	//                                                  in milliseconds (i.e. -5000 means
	//                                                  5 seconds ago).
	//                - A zero value (=0)             : No initial query time. All values until
	//                                                  lEnd will be provided.
	//
	//    lEnd    - The final query time. It can have the following values:
	//
	//                - A greater than zero value (>0): Represents a absolute UNIX time, in 
	//                                                  milliseconds (i.e. 1164368881325).
	//                - A lesser than zero value (<0) : A UNIX time, relative to the actual time
	//                                                  in milliseconds (i.e. -5000 means
	//                                                  5 seconds ago).
	//                - A zero value (=0)             : The actual time.
	//
	//    iWindow - The window size in milliseconds. the [lIni, lEnd] interval will be splited
	//              in subintervals of lWindow lenght, and one average value will be provided
	//              for each one.
	//
	//    sClient - The client_id value
	//

	public Vector<GValue> query(String sParam, String sHost, long lIni, long lEnd, String sClient) throws RemoteException {

		// Time interval adjustment
		long lInitial = lIni;
		long lFinal = lEnd;
		long currentT = System.currentTimeMillis();
		if (lIni < 0)
			lInitial = currentT + lIni;
		else if (lIni == 0)
			lInitial = bd.getOldestTime();

		if (lEnd <= 0)
			lFinal = currentT + lEnd;

		return bd.queryValues(sParam, sHost, lInitial, lFinal, sClient);
	}

	public Vector<GValue> query(String sParam, String sHost, long lIni, long lEnd) throws RemoteException {

		return query(sParam, sHost, lIni, lEnd, null);

	}

	public Vector<GValue> query(String sParam, long lIni, long lEnd) throws RemoteException {

		return query(sParam, null, lIni, lEnd, null);

	}

    public Vector<GValue> queryLast(String sParam, long lTime) throws RemoteException {
    	
    	return query(sParam, null, -1*lTime, 0, null);
    }

    // ----------------------------------------------------------------------------------------------

    public Vector<GValue> queryGlobal(String sParam, long lTime) throws RemoteException {
    	
    	Vector<GValue> result = new Vector<GValue>();
    	
    	Vector<GValue> values = query(sParam, null, -1*lTime, 0, null);
    	long time = values.lastElement().sTime;
    	 
       	GValue gV_avg = new GValue();
       	gV_avg.sName = sParam+"_avg";
       	gV_avg.sTime = time;
    	gV_avg.sValue = mean(values);
    	
    	result.add(gV_avg);

    	GValue gV_sd = new GValue();
       	gV_sd.sName = sParam+"_stdev";
       	gV_sd.sTime = time;
    	gV_sd.sValue = stdev(values);
    	
    	result.add(gV_sd);
    	
    	return result;
    }

    // ----------------------------------------------------------------------------------------------

    public GValue queryLastValue(String sParam, String sHost, String sClient) {

		//CValue res = null;

		return bd.queryLast(sParam, sHost, sClient);

	}

	public GValue queryLastValue(String sParam, String sHost) {

		return queryLastValue(sParam, sHost, "");

	}

	// ----------------------------------------------------------------------------------------------
	public void changeParameter (String sNombre, String sFuncion, String sHost){
		bd.changeP(sNombre, sFuncion, sHost);
	}

	// ----------------------------------------------------------------------------------------------
	// ----------------------------------------------------------------------------------------------
	// Subscriber attributes and operations

	// -----------------------------------------------------
	// Received Values vector and operations to access

	private Vector<GValue> valuesReceived = new Vector<GValue>();

	private synchronized void addPubValue(GValue value) {
		value.sTime = System.currentTimeMillis();
		valuesReceived.add(value);
	}

	private synchronized Vector<GValue> popPubValues() {

		Vector<GValue> res = new Vector<GValue>();

		for (int i = 0; i < valuesReceived.size(); i++) {
			res.add(valuesReceived.elementAt(i));
		}
		valuesReceived.removeAllElements();
		return res;
	}

	// -----------------------------------------------------

	public Vector<GValue> getSubscribedValues() {

		Vector<GValue> vals = popPubValues();

		return vals;
	}

	public void setSubscriptions(String[] subs) {
		subscriptions = subs;
	}
	
	public void storeSubscribedValue(GValue value) {

		addPubValue(value);
	}

	public void storeSubscribedValues(Vector<GValue> values) {

		//System.out.println("Receiving: "+values);
		for (int i = 0; i < values.size(); i++) {
			addPubValue(values.elementAt(i));
		}
	}

	// ----------------------------------------------------------------------------------------------

	private double mean(Vector<GValue> sample) {
		
		double acc = 0.0;

		for (int i = 0; i < sample.size(); i++) {
			double x = sample.elementAt(i).sValue;
			acc += x;
		}

		return (acc / sample.size());
	}
	
	private double variance(Vector<GValue> sample) {
		long n = 0;
		double mean = 0;
		double s = 0.0;

		for (int i = 0; i < sample.size(); i++) {
			double x = sample.elementAt(i).sValue;
			n++;
			double delta = x - mean;
			mean += delta / n;
			s += delta * (x - mean);
		}
		return (s / (n-1));
	}

	private double stdev(Vector<GValue> sample) {
		return Math.sqrt(variance(sample));
	}
	
	// ----------------------------------------------------------------------------------------------
	// ----------------------------------------------------------------------------------------------
	public static void main(String[] args) {
	}
}
