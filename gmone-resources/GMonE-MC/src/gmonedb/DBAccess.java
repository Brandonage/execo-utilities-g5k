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

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.Vector;
import java.io.*;
import common.*;

public class DBAccess implements Serializable {

	private static final long serialVersionUID = 1L;
	private String dbURL;
	private String jdbcDriver;
	//private Connection connection;
	//private Statement stmt;
	private boolean conectado = false;

	private boolean sqlite = false; // Se usa mysql por defecto

	private String mysql_user = "mon_user";
	private String mysql_pass = ".m0nalisa";

	public final static int MAX_CADENA = 1024;

	public final static int MAX_SERVERS = 1024;
	public final static int MAX_FILE_NAME_SIZE = 128;
	public final static int MAX_SERVICE_URI_SIZE = 256;
	//	private final static int MAX_SUB_GROUP_SIZE = MAX_SERVERS/6;


	// -----------------------------------------------------------
	// Constructor de la clase
	public DBAccess (String jDBCDriver, String dataBaseURL) {
		dbURL = dataBaseURL;
		jdbcDriver = jDBCDriver;
		//Configurator config = Configurator.getConfigurator();
		//mysql_user = config.getProperty("gmone2_user");
		//mysql_pass = config.getProperty("gmone2_pass");
		if (jdbcDriver.compareTo("org.sqlite.JDBC") == 0) {
			// Estamos usando sqlite
			sqlite = true;
		}
		conectarDB();
	}

	// Conexion a la base de datos
	private Statement connect() {

		Statement stmt = null;

		try {
			Connection connection = null;
			if (sqlite)
				connection = DriverManager.getConnection(dbURL);
			else
				connection = DriverManager.getConnection(dbURL, mysql_user, mysql_pass);

			stmt = connection.createStatement();

		} catch(java.sql.SQLException e) {
			System.err.println("ERROR!");
			e.getSQLState();
			e.printStackTrace();
		}

		return stmt;
	}

	private void conectarDB() {

		if (!conectado) {
			try{	
				Class.forName(jdbcDriver);
			}catch(java.lang.Exception e) {
				System.err.println("ERROR!");
				e.printStackTrace();
			}

			//this.stmt = connect();
			if (connect() != null)
				conectado = true;
		}		
	}


	// -----------------------------------------------------------
	public void createTables() {

		// ATENCION: Este metodo solo funciona con SQLite
		// Si se usa MySql hay que crear las tablas manualmente;

		if (sqlite) {
			Statement stmt = connect();
			try {

				stmt.executeUpdate("CREATE TABLE parameter " +
						"(name VARCHAR("+ MAX_CADENA +"), "+
						"host VARCHAR("+ MAX_CADENA +"), "+
						"func VARCHAR("+ MAX_CADENA +"))");

			} catch(java.sql.SQLException e) {
				//system.err.println("ERROR!");
				e.getSQLState();
				//e.printStackTrace();
			}

			try {

				stmt.executeUpdate("CREATE TABLE readings " +
						"(time INTEGER, "+
						"parameter VARCHAR("+ MAX_CADENA +"), "+
						"value FLOAT, "+
						"host VARCHAR("+ MAX_CADENA +"), "+
						"client_id VARCHAR("+ MAX_CADENA +"), "+
						"units VARCHAR("+ MAX_CADENA +"))");

			} catch(java.sql.SQLException e) {
				//system.err.println("ERROR!");
				e.getSQLState();
				//e.printStackTrace();
			}
		}
	}

	// -----------------------------------------------------------
	public synchronized void addParam(String param, String host, String func) {

		String query ="";		
		//int rs=0;

		Statement stmt = connect();

		try {
			query = "INSERT INTO parameter VALUES ('"+param+"', '"+host+"', '"+func+"')";
			//rs = 
			stmt.executeUpdate(query);
		} catch(java.sql.SQLException e) {
			System.err.println("ERROR!: "+query);
			e.getSQLState();
			e.printStackTrace();
		}
	}

	// -----------------------------------------------------------

	public synchronized int exeQueryWrite (String parametro, double valor, long time, String sHost, String sClient, String sUnits) {

		String query ="";		
		//String parametro="";
		//long valor=0;
		int rs=0;

		Statement stmt = connect();

		try {
			query = "INSERT INTO readings VALUES ("+time+", '"+parametro+"', "+valor+
			", '"+sHost+"', '"+sClient+"', '"+sUnits+"')";
			rs = stmt.executeUpdate(query);

			/*while (rs.next()){
	      i++;
	      System.out.println("\nEl valor "+i+" es "+rs.getString("name")+"\n");
	      }*/			
		} catch(java.sql.SQLException e) {
			System.err.println("ERROR!: "+query);
			e.getSQLState();
			e.printStackTrace();
		}
		return rs;
	}


	// -----------------------------------------------------------

	public synchronized int exeMultipleWrite (Vector<GValue> values, long time) {

		String query ="";		
		//String parametro="";
		//long valor=0;
		int rs=0;

		Statement stmt = connect();

		for (int i = 0; i < values.size(); i++) {

			GValue val = values.elementAt(i);

			try {
				query = "INSERT INTO readings VALUES ("+time+", '"+val.sName+"', "+val.sValue+
				", '"+val.sHost+"', '"+val.sInfo+"', '"+val.sUnits+"')";
				rs = stmt.executeUpdate(query);

				/*while (rs.next()){
		  i++;
		  System.out.println("\nEl valor "+i+" es "+rs.getString("name")+"\n");
		  }*/
			} catch(java.sql.SQLException e) {
				System.err.println("ERROR!: "+query);
				e.getSQLState();
				e.printStackTrace();
			}
		}
		return rs;
	}


	// -----------------------------------------------------------
	// -----------------------------------------------------------
	public synchronized Vector<GHost> leerParametros() {

		Statement stmt = connect();

		Vector<GHost> v = new Vector<GHost>();
		//CHost cH = new CHost();
		try {

			// Se leen los par?metros
			ResultSet rs = stmt.executeQuery("SELECT * FROM parameter");


			// Se almacenan en el vector
			while (rs.next()) {
				//String[] p = new String[3];
				GHost cH = new GHost();
				cH.name = new String (rs.getString("name"));
				cH.host = new String (rs.getString("host"));
				cH.func = new String (rs.getString("func"));
				v.add(cH);
			}

		} catch(java.sql.SQLException e) {
			System.err.println("ERROR!");
			e.getSQLState();
			e.printStackTrace();
		}

		// Se devuelve el valor
		return v;
	}

	/*public class CHost{
      public long sValue;
      public String sHost;
      }*/

	public synchronized Vector<GValue> queryValues (String sParam, String sHost, long lIn, long lEn, String sClient){

		Vector<GValue> res = new Vector<GValue>();
		String query = "SELECT * from readings WHERE parameter = '" + sParam +
		"' and time >= "+ lIn +" and time < "+ lEn;

		if (!(sHost == null))
			query = query + " and host = '"+sHost+"'";
		if (!(sClient == null))
			query = query + " and client_id = '"+sClient+"'";

		query = query + ";";

		//CHost cHost = new CHost();

		//if(sParam.equals("*")){
		//    query = "SELECT * from readings WHERE host = '"+ sHost +"'"+
		//	" and time >= "+ lIn +" and time < "+ lEn +";";
		//} else if ("".equals(sClient)) {
		//	query = "SELECT * from readings WHERE parameter = '" +
		//	    sParam +"' and host = '"+ sHost + "' and time >= "+ lIn +
		//	    " and time < "+ lEn +";";
		//} else {
		//	query = "SELECT * from readings WHERE parameter = '"+
		//	    sParam +"' and host = '"+ sHost +"' and client_id = '"+sClient +
		//	    "' and time >= "+ lIn +" and time < "+ lEn +";";			
		//}


		//ResultSet rs = executeQuery(query);
		ResultSet rs;
		Statement stmt = connect();	
		//long res_1;

		//System.out.println(query);

		try {

			rs = stmt.executeQuery(query);
			while (rs.next()){

				GValue val = new GValue();
				val.sName = rs.getString("parameter");
				val.sTime = rs.getLong("time");
				val.sValue = rs.getDouble("value");
				val.sHost = rs.getString("host");
				val.sInfo = rs.getString("client_id");
				val.sUnits = rs.getString("units");

				//Double temp = new Double(rs.getDouble("value"));
				//System.out.println("Valor leido en la BD: "+val.sValue+" ("+val.sTime+")");
				res.add(val);
			}


		} catch(java.sql.SQLException e) {
			//system.err.println("ERROR!");
			e.getSQLState();
			e.printStackTrace();
		}

		return res;
	}

	// -----------------------------------------------------------
	//	SELECT MAX(time),host FROM readings WHERE parameter = 'bw_read' GROUP BY host;

	public synchronized GValue consultLast (String sParam, String sHost, String sClient) {

		GValue val = null;
		String query = "";

		if ("".equals(sClient)) {
			query = "SELECT * FROM readings WHERE parameter = '" +
			sParam +"' and host = '"+ sHost + "' ORDER BY time DESC LIMIT 1"+
			";";
		} else {
			query = "SELECT * FROM readings WHERE parameter = '"+
			sParam +"' and host = '"+ sHost + "' and client_id = '"+sClient+"' "+
			"ORDER BY time DESC LIMIT 1" +
			";";
		}

		ResultSet rs;

		Statement stmt = connect();

		try {

			rs = stmt.executeQuery(query);
			if (rs.next()){

				val = new GValue();
				val.sTime = rs.getLong("time");
				val.sValue = rs.getDouble("value");
				val.sHost = rs.getString("host");
				val.sInfo = rs.getString("client_id");
				val.sUnits = rs.getString("units");

			}

		} catch(java.sql.SQLException e) {
			e.getSQLState();
			e.printStackTrace();
		}

		return val;

	}

	// -----------------------------------------------------------
	/**
	 * Returns the last average for a given parameter. The average is calculated with the las values
	 * of every host.
	 * @param parameter The name of the parameter we want to analyze
	 * @return The average, NaN if any error
	 * */
	public synchronized double getLastAvarage(String parameter){
		double average=Double.NaN;
		String query  = "SELECT avg ( t1.value ) AS media "+
		"FROM ("+
		"SELECT value, max(time) "+
		"FROM readings "+
		"WHERE parameter ='"+parameter+"' "+
		"GROUP BY host"+
		") AS t1 LIMIT 0 , 30";
		ResultSet rs;
		Statement stmt = connect();	

		try {

			rs = stmt.executeQuery(query);
			if (rs.next()){
				average = rs.getDouble("media");
			}
		}catch(java.sql.SQLException e) {
			e.getSQLState();
			e.printStackTrace();
		}
		return average;
	}

	// -----------------------------------------------------------

	public synchronized void changeP (String sNombre, String sFuncion, String sHost){

		// TO DO an update into table parameters with the new function
		// asociated to a parameter in a host.
		String query ="";		
		//String parametro="";
		//long valor=0;
		//		int rs=0;

		Statement stmt = connect();

		try {
			query = "UPDATE parameter set func = '"+sFuncion+"' where host = '"+sHost+"' and name = '"+sNombre+"';";
			stmt.executeUpdate(query);

		} catch(java.sql.SQLException e) {
			//system.err.println("ERROR!");
			e.getSQLState();
			e.printStackTrace();
		}

		//return rs;

	}


	public synchronized long getOldestTime() {

		String query = "";
		//CHost cHost = new CHost();

		query = "SELECT MIN(time) from readings;";

		ResultSet rs;
		Statement stmt = connect();
		long res = 0;

		//System.out.println(query);

		try {

			rs = stmt.executeQuery(query);
			if (rs.next()){
				res = rs.getLong("MIN(time)");
			}


		} catch(java.sql.SQLException e) {
			//system.err.println("ERROR!");
			e.getSQLState();
			e.printStackTrace();
		}

		return res;

	}

	// -----------------------------------------------------------

	public synchronized Vector<String> readParams() {
		
		Vector<String> res = new Vector<String>();
		String query = "SELECT parameter FROM readings GROUP BY parameter;";
		ResultSet rs;
		Statement stmt = connect();
		try {
			rs = stmt.executeQuery(query);
			while (rs.next()){
				String param = new String(rs.getString("parameter"));
				res.add(param);
			}
		} catch(java.sql.SQLException e) {
			e.getSQLState();
			e.printStackTrace();
		}
		
		return res;
		
	}
	
	// -----------------------------------------------------------

	public synchronized Vector<String> readHosts() {
		
		Vector<String> res = new Vector<String>();
		String query = "SELECT host FROM readings GROUP BY host;";
		ResultSet rs;
		Statement stmt = connect();
		try {
			rs = stmt.executeQuery(query);
			while (rs.next()){
				String host = new String(rs.getString("host"));
				res.add(host);
			}
		} catch(java.sql.SQLException e) {
			e.getSQLState();
			e.printStackTrace();
		}
		
		return res;
		
	}
	
}
