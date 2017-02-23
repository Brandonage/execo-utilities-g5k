package gmonedb;

import java.io.UnsupportedEncodingException;
import java.nio.ByteBuffer;
import java.util.Vector;
//import java.util.List;

import org.apache.cassandra.thrift.Cassandra;
import org.apache.cassandra.thrift.Column;
//import org.apache.cassandra.thrift.ColumnOrSuperColumn;
import org.apache.cassandra.thrift.ColumnParent;
//import org.apache.cassandra.thrift.ColumnPath;
import org.apache.cassandra.thrift.ConsistencyLevel;
//import org.apache.cassandra.thrift.InvalidRequestException;
//import org.apache.cassandra.thrift.NotFoundException;
//import org.apache.cassandra.thrift.SlicePredicate;
//import org.apache.cassandra.thrift.SliceRange;
//import org.apache.cassandra.thrift.TimedOutException;
//import org.apache.cassandra.thrift.UnavailableException;
//import org.apache.thrift.TException;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TFramedTransport;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransport;
//import org.apache.thrift.transport.TTransportException;

import common.GMonELogger;
import common.GValue;

public class DBAccessCassandra implements DBAccessInterface {

	private Cassandra.Client client;
	private String cassandraHost = "localhost";
	private int cassandraPort = 9160;
	
	//-----------------------------------------------------------------------------

	public DBAccessCassandra() {
		init();
	}
	
	public DBAccessCassandra(String host, int port) {
		cassandraHost = host;
		cassandraPort = port;
		init();
	}

	//-----------------------------------------------------------------------------

	private void init() {
        try {
        	GMonELogger.message("Connecting to Cassandra at "+cassandraHost+":"+cassandraPort);
        	TTransport tr = new TFramedTransport(new TSocket(cassandraHost, cassandraPort));
        	TProtocol proto = new TBinaryProtocol(tr);
        	client = new Cassandra.Client(proto);
			tr.open();
        	GMonELogger.message("Selecting Cassandra key space GMonE");
        	client.set_keyspace("GMonE");
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	//-----------------------------------------------------------------------------

	@Override
	public Vector<String> readParams() {
		// TODO Auto-generated method stub
		GMonELogger.message("WARNING: Method readParams not implemented!!");
		return null;
	}

	//-----------------------------------------------------------------------------

	@Override
	public Vector<String> readHosts() {
		// TODO Auto-generated method stub
		GMonELogger.message("WARNING: Method readHosts not implemented!!");
		return null;
	}

	//-----------------------------------------------------------------------------

	@Override
	public Vector<GValue> queryValues(String sParam, String sHost, long lIn, long lEn, String sClient) {
		// TODO Auto-generated method stub
		GMonELogger.message("WARNING: Method queryValues not implemented!!");
		return null;
	}

	//-----------------------------------------------------------------------------

	@Override
	public long getOldestTime() {
		// TODO Auto-generated method stub
		GMonELogger.message("WARNING: Method getOldestTime not implemented!!");
		return 0;
	}

	//-----------------------------------------------------------------------------

	@Override
	public GValue queryLast(String sParam, String sHost, String sClient) {
		// TODO Auto-generated method stub
		GMonELogger.message("WARNING: Method queryLast not implemented!!");
		return null;
	}

	//-----------------------------------------------------------------------------

	@Override
	public void changeP(String sNombre, String sFuncion, String sHost) {
		// TODO Auto-generated method stub
		GMonELogger.message("WARNING: Method changeP not implemented!!");
	}

	//-----------------------------------------------------------------------------

	public void exeQueryWrite (String parameter, double value, long time, String host, String info, String units) { 

		ColumnParent parent = new ColumnParent("readings");
		String key = host+"_"+parameter+"_"+time;
		
        try {
			Column timeColumn = new Column(toByteBuffer("time"));
			timeColumn.setValue(toByteBuffer(""+time));
	        timeColumn.setTimestamp(time);
			client.insert(toByteBuffer(key), parent, timeColumn, ConsistencyLevel.ONE);
			
			Column paramColumn = new Column(toByteBuffer("parameter"));
			paramColumn.setValue(toByteBuffer(parameter));
	        paramColumn.setTimestamp(time);
			client.insert(toByteBuffer(key), parent, paramColumn, ConsistencyLevel.ONE);

			Column valueColumn = new Column(toByteBuffer("value"));
			valueColumn.setValue(toByteBuffer(""+value));
	        valueColumn.setTimestamp(time);
			client.insert(toByteBuffer(key), parent, valueColumn, ConsistencyLevel.ONE);

			Column hostColumn = new Column(toByteBuffer("host"));
			hostColumn.setValue(toByteBuffer(host));
	        hostColumn.setTimestamp(time);
			client.insert(toByteBuffer(key), parent, hostColumn, ConsistencyLevel.ONE);

			Column infoColumn = new Column(toByteBuffer("info"));
			infoColumn.setValue(toByteBuffer(info));
	        infoColumn.setTimestamp(time);
			client.insert(toByteBuffer(key), parent, infoColumn, ConsistencyLevel.ONE);

			Column unitsColumn = new Column(toByteBuffer("units"));
			unitsColumn.setValue(toByteBuffer(units));
	        unitsColumn.setTimestamp(time);
			client.insert(toByteBuffer(key), parent, unitsColumn, ConsistencyLevel.ONE);

        } catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	@Override
	public int exeMultipleWrite(Vector<GValue> values) {
		
		for (int i = 0; i < values.size(); i++) {
			GValue value = values.elementAt(i);
			exeQueryWrite(value.sName, value.sValue, value.sTime, value.sHost, value.sInfo, value.sUnits);
		}
		return 0;
	}

	//-----------------------------------------------------------------------------

    public static ByteBuffer toByteBuffer(String value) 
    throws UnsupportedEncodingException
    {
    	ByteBuffer res = ByteBuffer.wrap("".getBytes("UTF-8"));
    	if (value != null)
    		res = ByteBuffer.wrap(value.getBytes("UTF-8"));
    	return res;
    }
        
    public static String toString(ByteBuffer buffer) 
    throws UnsupportedEncodingException
    {
        byte[] bytes = new byte[buffer.remaining()];
        buffer.get(bytes);
        return new String(bytes, "UTF-8");
    }
	
	//-----------------------------------------------------------------------------
	//-----------------------------------------------------------------------------
	//-----------------------------------------------------------------------------
	
	/*
    public static void main(String[] args)
    throws TException, InvalidRequestException, UnavailableException, UnsupportedEncodingException, NotFoundException, TimedOutException
    {
        TTransport tr = new TFramedTransport(new TSocket("localhost", 9160));
        TProtocol proto = new TBinaryProtocol(tr);
        Cassandra.Client client = new Cassandra.Client(proto);
        tr.open();

        String key_user_id = "1";

        // insert data
        long timestamp = System.currentTimeMillis();
        client.set_keyspace("Keyspace1");      
        ColumnParent parent = new ColumnParent("Standard1");

        Column nameColumn = new Column(toByteBuffer("name"));
        nameColumn.setValue(toByteBuffer("Chris Goffinet"));
        nameColumn.setTimestamp(timestamp);
        client.insert(toByteBuffer(key_user_id), parent, nameColumn, ConsistencyLevel.ONE);
        
        Column ageColumn = new Column(toByteBuffer("age"));
        ageColumn.setValue(toByteBuffer("24"));
        ageColumn.setTimestamp(timestamp);
        client.insert(toByteBuffer(key_user_id), parent, ageColumn, ConsistencyLevel.ONE);

        ColumnPath path = new ColumnPath("Standard1");

        // read single column
        path.setColumn(toByteBuffer("name"));
        System.out.println(client.get(toByteBuffer(key_user_id), path, ConsistencyLevel.ONE));

        // read entire row
        SlicePredicate predicate = new SlicePredicate();
        SliceRange sliceRange = new SliceRange(toByteBuffer(""), toByteBuffer(""), false, 10);
        predicate.setSlice_range(sliceRange);
        
        List<ColumnOrSuperColumn> results = client.get_slice(toByteBuffer(key_user_id), parent, predicate, ConsistencyLevel.ONE);
        for (ColumnOrSuperColumn result : results)
        {
            Column column = result.column;
            System.out.println(toString(column.name) + " -> " + toString(column.value));
        }

        tr.close();
    }
    */
}
