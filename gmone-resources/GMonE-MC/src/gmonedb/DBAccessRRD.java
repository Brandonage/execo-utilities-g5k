package gmonedb;

import java.awt.Color;
import java.io.File;
//import java.io.IOException;
import java.util.Vector;

import org.rrd4j.core.*;
import org.rrd4j.graph.RrdGraph;
import org.rrd4j.graph.RrdGraphDef;

import static org.rrd4j.ConsolFun.*;
import static org.rrd4j.DsType.GAUGE;

import common.GMonELogger;
import common.GValue;

public class DBAccessRRD implements DBAccessInterface {

	private String rrdBaseDir = "./";
	private boolean plot = false;
	
	static final int IMG_WIDTH = 500;
    static final int IMG_HEIGHT = 300;
	
	//-----------------------------------------------------------------------------

	public DBAccessRRD() {
		GMonELogger.message("Storing RRD files at "+rrdBaseDir);
	}

	public DBAccessRRD(String rrdDir, boolean plot) {
		this.rrdBaseDir = rrdDir;
		this.plot = plot;
		GMonELogger.message("Storing RRD files at "+rrdBaseDir);
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

	private RrdDb getRRD(String path, String parameter, long time) {
		
		RrdDb result = null;		
		try {
			File f = new File(path);
			if (! f.exists()) {
				GMonELogger.message("Creating "+path);
				RrdDef rrdDef = new RrdDef(path, 1);
				rrdDef.setStartTime((time/1000)-1);
				rrdDef.addDatasource(parameter, GAUGE, 600, Double.MIN_VALUE, Double.MAX_VALUE);
				rrdDef.addArchive(LAST, 0.5, 1, 3600);
				result = new RrdDb(rrdDef);
				GMonELogger.message(path+" created.");
			} else {
				result = new RrdDb(path);
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
		return result;
	}
	
	public boolean exeQueryWrite (String parameter, double value, long time, String host, String info, String units) { 

		String rrdPath = rrdBaseDir+"/"+host+"_"+parameter+".rrd";
		boolean discarded = false;
		
        try {
    		// Getting RRD file
    		RrdDb rrd = getRRD(rrdPath, parameter, time);
    		
    		// Inserting value
    		Sample sample = rrd.createSample();
    		sample.setTime(time/1000);
    		sample.setValue(parameter, value);
    		sample.update();
    		
    		if (plot) {
				long end = rrd.getLastArchiveUpdateTime();
				long start = end - 3600;
				GMonELogger.message("Generating plot for " + rrdPath + " ["
						+ start + "," + end + "]");
				RrdGraphDef gDef = new RrdGraphDef();
				gDef.setWidth(500);
				gDef.setHeight(300);
				gDef.setFilename(rrdPath + ".png");
				gDef.setStartTime(start);
				gDef.setEndTime(end);
				gDef.setTitle(parameter);
				gDef.setVerticalLabel(units);
				gDef.datasource(parameter, rrdPath, parameter, LAST);
				gDef.line(parameter, Color.BLACK, parameter);
				//gDef.hrule(2568, Color.GREEN, "hrule");
				//gDef.vrule(((rrd.getLastArchiveUpdateTime()-99) + 2 * rrd.getLastArchiveUpdateTime()) / 3, Color.MAGENTA, "vrule\\c");
				gDef.comment("\\r");
				gDef.gprint(parameter, LAST, parameter + " = %.3f%s");
				gDef.setImageInfo("<img src='%s' width='%d' height = '%d'>");
				gDef.setPoolUsed(false);
				gDef.setImageFormat("png");
				//RrdGraph graph = new RrdGraph(gDef);
				new RrdGraph(gDef);
				//System.out.println(graph.getRrdGraphInfo().dump());
			}
			rrd.close();
    		//GMonELogger.message("Value stored in "+rrdPath);
        } catch (IllegalArgumentException ie) {
        	//ie.printStackTrace();
        	discarded = true;
        } catch (Exception e) {
			e.printStackTrace();
		}
        return discarded;
	}

	@Override
	public int exeMultipleWrite(Vector<GValue> values) {
		
		boolean discarded = false;
		for (int i = 0; i < values.size(); i++) {
			GValue value = values.elementAt(i);
			discarded = exeQueryWrite(value.sName, value.sValue, value.sTime, value.sHost, value.sInfo, value.sUnits);
		}
		if (discarded)
			GMonELogger.message("RRD WARNING: Some values discarded (timestamps too close for the same host+parameter).");

		return 0;
	}

}
