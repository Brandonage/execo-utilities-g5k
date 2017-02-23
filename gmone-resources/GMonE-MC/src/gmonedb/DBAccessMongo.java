package gmonedb;

import com.mongodb.client.FindIterable;
import common.GMonELogger;
import common.GValue;
import com.mongodb.MongoClient;
import com.mongodb.client.MongoDatabase;

import java.util.ArrayList;
import java.util.List;
import java.util.Vector;
import org.bson.Document;
import com.mongodb.Block;

import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Locale;

import static java.util.Arrays.asList;

/**
 * Created by alvarobrandon on 03/05/16.
 */
public class DBAccessMongo implements DBAccessInterface {

    private MongoClient client;
    private MongoDatabase db;
    private String mongoHost = "localhost";
    private int mongoPort = 27017;

    //-----------------------------------------------------------------------------

    public DBAccessMongo() {
        init();
    }

    public DBAccessMongo(String host, int port) {
        mongoHost = host;
        mongoPort = port;
        init();
    }

    //-----------------------------------------------------------------------------

    private void init() {
        try {
            client = new MongoClient(mongoHost,mongoPort);
            db = client.getDatabase("gmone");

            //Connect to MongoDB , select the DB, ¿Meteor? and create indexes
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

        try {
            db.getCollection("readings").insertOne(
                    new Document("parameter",parameter)
                    .append("value",value)
                    .append("time",time)
                    .append("host",host)
                    .append("info",info)
                    .append("units",units)
            );


            //INSERT ALL THE VALUES THAT WE WANT

        } catch (Exception e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
    }

    @Override
    public int exeMultipleWrite(Vector<GValue> values) {
        List<Document> docs = new ArrayList<Document>();

        for (int i = 0; i < values.size(); i++) {
            GValue value = values.elementAt(i);
            docs.add(new Document("parameter",value.sName)
                    .append("value",value.sValue)
                    .append("time",value.sTime)
                    .append("host",value.sHost)
                    .append("info",value.sInfo)
                    .append("units",value.sUnits));
        }
        db.getCollection("readings").insertMany(docs);
        return 0;
    }

    //-----------------------------------------------------------------------------

    public void test() {
        GMonELogger.message("Inserting Many Documents in MongoDB...");
        Vector<GValue> values = new Vector<GValue>();
        for (int i = 0; i < 12; i++){
            GValue cV = new GValue();
            cV.sName = "parameter" + i;
            cV.sValue = 10;
            values.add(cV);
        }
        exeMultipleWrite(values);
        GMonELogger.message("Batch of Documents inserted in MongoDB...");


        GMonELogger.message("Inserting One Document in MongoDB...");
        this.exeQueryWrite("parameter1",10,1234812394,"saggitaire.45",null,"KB");
        GMonELogger.message("Document inserted in MongoDB... Querying data now");
        FindIterable<Document> iterable = db.getCollection("readings").find();
        iterable.forEach(new Block<Document>() {
            @Override
            public void apply(final Document document) {
                System.out.println(document);
            }
        });
    }

    public static void main(String[] args){
        DBAccessMongo mongoAcc = new DBAccessMongo("localhost",27017);
        mongoAcc.test();
    }

}
