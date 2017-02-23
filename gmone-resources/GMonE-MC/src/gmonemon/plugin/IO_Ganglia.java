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
	
package gmonemon.plugin;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.StringReader;
import java.net.InetAddress;
import java.net.Socket;
import java.util.Vector;

public class IO_Ganglia {

	/*static String[] metric={"cpu_num","cpu_user","cpu_system","cpu_idle","cpu_speed","disk_total","disk_free",
      "bytes_in","bytes_out","load_five","proc_run", "mem_free"}; 
	 */
	//String ruta = "/home/laurel/alum/eperez/workspace3/Ganglia_Varios/prueba/params.txt";
	String ruta;

	static String[] ReadFich (String nameFile){
		String[] metric={null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null};
		BufferedReader reader;
		try {
			reader = new BufferedReader(new FileReader(nameFile));
			try {
				String linea= reader.readLine();
				//String linea2= reader.readLine();
				int i=0;
				while(linea!=null) {
					if ((linea.charAt(0)!='#') && (linea.length()!=0))
						metric[i]=linea;
					//System.out.println(linea); 
					linea= reader.readLine();
					if(linea!=null)
						//linea2= 
						reader.readLine();
					i++;
				}
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		} catch (FileNotFoundException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}

		return metric;
	}

	//static String[] metric = ReadFich("params.txt");
	static String[] metric;

	static String host;
	static int port;


	public IO_Ganglia(String sHost, int iPort, String sRuta) {
		super();
		host = sHost;
		port = iPort;
		ruta = sRuta;

		// TODO Auto-generated constructor stub
	}

	//public static BufferedReader TcpCmd(String host, int port, String cmd) {
	public BufferedReader TcpCmd(String host, int port, String cmd) {

		InetAddress remote = null;
		Socket socket = null;
		OutputStreamWriter out = null;
		BufferedInputStream buffer = null;
		InputStreamReader in = null;

		//Create the sock
		try {
			remote = InetAddress.getByName(host);
			socket = new Socket(remote, port);
			socket.setSoTimeout(1000);
			socket.setSoLinger(true, 1);
			socket.setTcpNoDelay(true);
		} catch (Throwable t) {
			t.printStackTrace();
			cleanup(socket, in, out, buffer);
			return null;
		}

		try {

			out = new OutputStreamWriter(socket.getOutputStream(), "8859_1");
			buffer = new BufferedInputStream(socket.getInputStream());
			in = new InputStreamReader(buffer, "8859_1");

		} catch (Throwable t) {
			t.printStackTrace();
			cleanup(socket, in, out, buffer);
			return null;
		}

		try {

			out.write(cmd);
			out.flush();

			// read the result the return from the reflector
			StringBuffer answerBuff = new StringBuffer(1024);
			int c = in.read();
			while (c > -1 ) {
				//filter non-printable and non-ASCII
				if ((c >= 32 && c < 127)
						|| c == '\t'
							|| c == '\r'
								|| c == '\n') {

					answerBuff.append((char) c);
				}

				c = in.read();
			}

			cleanup(socket, in, out, buffer);

			return new BufferedReader(new StringReader(answerBuff.toString()));

		} catch ( Throwable t ) {
			t.printStackTrace();
			cleanup(socket, in, out, buffer);
			return null;
		}

	}
	private static void cleanup(
			Socket socket,
			InputStreamReader in,
			OutputStreamWriter out,
			BufferedInputStream buffer) {

		try {

			if (out != null)
				out.close();
			if (in != null)
				in.close();
			if (buffer != null)
				buffer.close();

		} catch (Throwable t) {
		}

		try {
			if (socket != null)
				socket.close();
		} catch (Throwable t) {
		}

	}

	public class CMetric{
		public String sName;
		public double sValue;
		public String sUnits;
	}


	public class CNode{
		public String NodeName;
		public long time;
		public Vector<CMetric> vMetrics= new Vector<CMetric>();
	};

	public Vector<CNode> Parse (  BufferedReader buff )   throws Exception  {
		int i1, i2;
		CNode rr = null ;
		Vector<CNode> CNodes = new Vector<CNode>() ;
		//metric = ReadFich(ruta);
		try {
			for ( ; ; ) {
				String lin = buff.readLine();
				if ( lin == null ) break;

				if ( lin.indexOf ("<HOST") != -1 ) {
					i1 = lin.indexOf ("=");
					i2 = lin.indexOf ("\"", i1+2 );

					rr = new CNode(); 
					rr.NodeName = lin.substring( i1+2, i2 );
					i1 = lin.indexOf ( "ED=" );
					i2 = lin.indexOf ( "\"",i1+4);
					long time = (new Long ( lin.substring(i1+4,i2 ))).longValue();
					rr.time =  time * 1000;

				} else  {
					if ( lin.indexOf ("/HOST>") != -1 ) {
						if ( rr != null ) CNodes.add(rr);
					} else {

						//int l=0;
						//while (metric[l]!=null){	
						if ( lin.indexOf ("<METRIC") != -1 ) {			    

							i1 = lin.indexOf ( "NAME=" ) ;
							i2 = lin.indexOf ( "\"", i1+6 ) ;
							String spar = lin.substring(i1+6,i2 ) ;

							i1 = lin.indexOf ( "VAL=" ) ;
							i2 = lin.indexOf ( "\"", i1+5 ) ;
							String sval = lin.substring(i1+5,i2 ) ;

							i1 = lin.indexOf ( "UNITS=" ) ;
							i2 = lin.indexOf ( "\"", i1+7 ) ;
							String sunits = lin.substring(i1+7,i2 ) ;

							if (sunits.equals("bytes/sec"))
								sunits = new String("B/s");

							try {
								//double val = (new Double ( lin.substring(i1+5,i2 ))).doubleValue();
								/*
				// trasform IO measurments in mb/s !
				if ( spar.indexOf( "bytes" ) != -1 ) { 
				    val = val*8/1000000.0;
				}
				// converet memory units from KB in MB 
				if ( spar.indexOf( "mem" ) != -1 ) {
				    val = val/1000.0;
				}
								 */

								//System.out.println(spar+", "+sval+", "+sunits);

								CMetric cMet = new CMetric();
								cMet.sName = spar;
								cMet.sValue = Double.parseDouble(sval);
								cMet.sUnits = sunits;
								rr.vMetrics.add(cMet);
							} catch (java.lang.NumberFormatException nex) {
								//System.out.println ("WARNING: parameter "+spar+" has not a numeric value. Ignoring");
							}
						}
						//l++;
						//}

					}

				}

			} 
			buff.close();
			//if ( pro != null ) pro.destroy();

		} catch ( Exception e ) { 
			e.printStackTrace();
			System.out.println ( "Exception in Get Ganglia"); 
			buff.close();
			//if ( pro != null ) pro.destroy();
			//throw e;
		}

		//System.out.println ( CNodes.size() );
		return CNodes;

	}
	/*
      public MonModuleInfo getInfo(){
      return info;
      }
      public String[] ResTypes () {
      return tmetric;
      }*/
	public String getOsName() { return "linux"; }

	public static void Imprimir(Vector<CNode> v){
		int i = 0;
		while (i< v.size()){
			CNode rr = (CNode)v.get(i);
			System.out.println("-----------------------------------------------");
			System.out.println("NODO: "+rr.NodeName+" ("+rr.time+")");
			int j = 0;
			while (j<rr.vMetrics.size()){
				CMetric cMet = (CMetric)rr.vMetrics.get(j);
				//System.out.println(metric[l]+" : "+val);
				System.out.println(cMet.sName+" : "+cMet.sValue);
				j++;
			}
			i++;
		}
	}
}
