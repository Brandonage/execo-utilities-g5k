package gmonedb;

import java.util.Vector;

import common.GValue;

public interface DBAccessInterface {

	public Vector<String> readParams();
	public Vector<String> readHosts();
	public Vector<GValue> queryValues (String sParam, String sHost, long lIn, long lEn, String sClient);
	public long getOldestTime();
	public GValue queryLast (String sParam, String sHost, String sClient);
	public void changeP (String sNombre, String sFuncion, String sHost);
	public int exeMultipleWrite (Vector<GValue> values);
}
