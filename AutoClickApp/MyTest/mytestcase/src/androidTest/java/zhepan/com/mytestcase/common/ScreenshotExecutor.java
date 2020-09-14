package zhepan.com.mytestcase.common;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Rect;
import android.os.Environment;
import android.support.test.uiautomator.UiDevice;
import android.util.Log;

import java.io.File;
import java.io.FileOutputStream;

public class ScreenshotExecutor {
    private static final String BASE_PATH = Environment.getExternalStorageDirectory().getAbsolutePath()
            + File.separator + "auto_test" + File.separator;
    private static final String SCREENSHOT_PATH = BASE_PATH + "screenshot.jpg";

    private UiDevice mDevice;

    public ScreenshotExecutor(UiDevice mDevice) {
        this.mDevice = mDevice;
    }

    public String takeElementShotByDefault(Rect rect) {
        try {
            File file = new File(SCREENSHOT_PATH);
            mDevice.takeScreenshot(file);

            BitmapFactory.Options bfOptions = new BitmapFactory.Options();
            bfOptions.inDither = false;
            bfOptions.inTempStorage = new byte[12 * 1024];
            bfOptions.inJustDecodeBounds = true;
            Bitmap bitmap = BitmapFactory.decodeFile(SCREENSHOT_PATH);
            bitmap = bitmap.createBitmap(bitmap, rect.left, rect.top, rect.width(), rect.height());//获取区域

            File filePic = new File(SCREENSHOT_PATH);

            if (!filePic.exists()) {
                filePic.createNewFile();
            }
            FileOutputStream fos = new FileOutputStream(SCREENSHOT_PATH);
            bitmap.compress(Bitmap.CompressFormat.JPEG, 100, fos);
            fos.flush();
            fos.close();
            return SCREENSHOT_PATH;
        } catch (Exception e) {
            Log.e("test","Exception occurred when take screenshot.");
            return null;
        }
    }

    public String takeElementShot(Rect rect, String...paths) {

        if (paths == null || paths.length < 1) {
            throw new IllegalArgumentException("path should not be empty.");
        }
        try {
            File file = new File(paths[0]);
            mDevice.takeScreenshot(file);

            BitmapFactory.Options bfOptions = new BitmapFactory.Options();
            bfOptions.inDither = false;
            bfOptions.inTempStorage = new byte[12 * 1024];
            bfOptions.inJustDecodeBounds = true;
            Bitmap bitmap = BitmapFactory.decodeFile(paths[0]);
            bitmap = bitmap.createBitmap(bitmap, rect.left, rect.top, rect.width(), rect.height());//获取区域

            String jpgCutPath = paths.length > 1 ? paths[1] : paths[0];
            File filePic = new File(jpgCutPath);

            if (!filePic.exists()) {
                filePic.createNewFile();
            }
            FileOutputStream fos = new FileOutputStream(jpgCutPath);
            bitmap.compress(Bitmap.CompressFormat.JPEG, 100, fos);
            fos.flush();
            fos.close();
            return filePic.getAbsolutePath();
        } catch (Exception e) {
            return null;
        }
    }

}
