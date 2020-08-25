package zhepan.com.mytestcase.common;

import android.os.Environment;
import android.util.Log;

import com.googlecode.tesseract.android.TessBaseAPI;

import java.io.File;

public class OcrExecutor {
    private static final String BASE_PATH = Environment.getExternalStorageDirectory().getAbsolutePath()
            + File.separator + "auto_test";
    private static final String DEFAULT_LANGUAGE = "chi_sim";

    private TessBaseAPI tessBaseAPI;

    public OcrExecutor() {
        tessBaseAPI = new TessBaseAPI();
        tessBaseAPI.init(BASE_PATH, DEFAULT_LANGUAGE);
    }

    public OcrExecutor(String dataPath, String defaultLanguage) {
        tessBaseAPI = new TessBaseAPI();
        tessBaseAPI.init(dataPath, defaultLanguage);
    }

    public String contentRecognize(String picPath) {
        File bitmap = new File(picPath);
        tessBaseAPI.setImage(bitmap);
        String text = tessBaseAPI.getUTF8Text();
        Log.i("test", "result: " + text);
        return text;
    }
}
