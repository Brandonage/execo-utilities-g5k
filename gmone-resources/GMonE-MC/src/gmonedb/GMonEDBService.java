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

import java.io.FileInputStream;
import java.util.Properties;

import common.GMonELogger;

public class GMonEDBService {

	public GMonEDBService() {
		super();
	}

	public static void main(String[] args) {

		//if (args.length == 2) {
		try {		
			// arg[0] -> periodo de muestreo.
			// arg[1] -> periodo de muestreo.
			// args[2] -> nombre de la base de datos 

			if (args.length != 2) {
				//System.out.println("Parameters: <hostname> <time_period> <database> [-passive]");
				System.out.println("Parameters: <host> <config file>");
				return;
			}

			String sHost = args[0];
			
		    Properties configFile = new Properties();
		    configFile.load(new FileInputStream(args[1]));
		    //boolean configError = false;

		    // Config file is assumed to be correct
			int period = Integer.parseInt(configFile.getProperty("period"));
			String dbmode = configFile.getProperty("dbmode");
			GMonELogger.message("Configurign access to the storage layer...");
			DBAccessInterface dbAccess = null;
			if (dbmode.equals("cassandra")) {
				String cassandraHost = configFile.getProperty("cassandra_host");
				int cassandraPort = Integer.parseInt(configFile.getProperty("cassandra_port"));
				dbAccess = (DBAccessInterface) new DBAccessCassandra(cassandraHost, cassandraPort); 
			} else if (dbmode.equals("sqlite")) {
				String sqliteDB = configFile.getProperty("sqlite_file");
				dbAccess = (DBAccessInterface) new DBAccessSQL("org.sqlite.JDBC", "jdbc:sqlite:"+sqliteDB);
			} else if (dbmode.equals("mysql")) {
				String mysqlDB = configFile.getProperty("mysql_db");
				dbAccess = (DBAccessInterface) new DBAccessSQL("com.mysql.jdbc.Driver", mysqlDB);
			} else if (dbmode.equals("rrd")) {
				String rrdDir = configFile.getProperty("rrd_dir");
				boolean plotParams = Boolean.parseBoolean(configFile.getProperty("rrd_plot"));
				dbAccess = (DBAccessInterface) new DBAccessRRD(rrdDir, plotParams);
			} else if (dbmode.equals("mongodb")) {
				String mongoHost = configFile.getProperty("mongo_host");
				int mongoPort = Integer.parseInt(configFile.getProperty("mongo_port"));
				dbAccess = (DBAccessInterface) new DBAccessMongo(mongoHost, mongoPort);
			}


			String[] subscriptions = configFile.getProperty("subscriptions").split(",");
			
			GMonELogger.message("Creating GMonEAccess...");
			GMonEAccess m = new GMonEAccess(sHost, dbAccess);
			m.setPeriod(period);
			m.setSubscriptions(subscriptions);
			m.startService();

		} catch (Exception e) {
			e.printStackTrace();
		}

	}
}

