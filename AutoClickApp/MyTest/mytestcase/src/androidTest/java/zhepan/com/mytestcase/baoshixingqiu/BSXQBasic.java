package zhepan.com.mytestcase.baoshixingqiu;

import android.graphics.Rect;
import android.os.Environment;
import android.support.test.uiautomator.UiDevice;
import android.support.test.uiautomator.UiObject;
import android.support.test.uiautomator.UiObjectNotFoundException;
import android.support.test.uiautomator.UiSelector;
import android.util.Log;

import java.io.File;

import zhepan.com.mytestcase.common.Constant;
import zhepan.com.mytestcase.common.FileOperator;
import zhepan.com.mytestcase.common.OcrExecutor;
import zhepan.com.mytestcase.common.ScreenshotExecutor;

public class BSXQBasic {
    private static final String BASE_PATH = Environment.getExternalStorageDirectory().getAbsolutePath()
            + File.separator + "auto_test" + File.separator;

    private UiDevice mDevice;
    private OcrExecutor ocrExecutor;
    private ScreenshotExecutor screenshotExecutor;

    public BSXQBasic(UiDevice mDevice) {
        this.mDevice = mDevice;
        screenshotExecutor = new ScreenshotExecutor(mDevice);
        ocrExecutor = new OcrExecutor();
    }

    public boolean collectPower() {
        UiObject x = mDevice.findObject(new UiSelector().text("宝石星球"));
        try {
            x.clickAndWaitForNewWindow();
        } catch (UiObjectNotFoundException e) {
            Log.i("test", "UiObjectNotFoundException: " + e);
            FileOperator.logToFile("[Failed|BSXQ] UiObjectNotFoundException");
            return false;
        }

        int i = 10;
        while(--i > 0) {
            try {
                Thread.sleep(3000);
            } catch (InterruptedException e) {
                return false;
            }
            if(checkForMainPage()) {
                FileOperator.logToFile("[Info|BSXQ] Open app successfully.");
                break;
            } else {
                FileOperator.logToFile("[Info|BSXQ] Waiting for open app.");
            }
        }
        if(i == 0) {
            FileOperator.logToFile("[Failed|BSXQ] Open app with timeout.");
            return false;
        }
        Rect rect = new Rect();
        rect.left = 170;
        rect.bottom = 1120 + Constant.Y_OFFSET;
        rect.right = 610;
        rect.top = 870 + Constant.Y_OFFSET;

        String path = screenshotExecutor.takeElementShotByDefault(rect);
        if(path == null) {
            return false;
        }
        String result = ocrExecutor.contentRecognize(path);
        if(result.contains("登录")) {
            return false;
        }
        if(result.contains("收获")) {
            mDevice.click(392 + Constant.X_OFFSET, 1054 + Constant.Y_OFFSET);
            if(checkCollectionSuccess(rect)) {
                FileOperator.logToFile("[Info|BSXQ] Collect power successfully.");
            }
        } else {
            mDevice.pressBack();
            path = screenshotExecutor.takeElementShotByDefault(rect);
            if(path == null) {
                return false;
            }
            result = ocrExecutor.contentRecognize(path);
            if(result.contains("收获")) {
                mDevice.click(392 + Constant.X_OFFSET, 1054 + Constant.Y_OFFSET);
                if(checkCollectionSuccess(rect)) {
                    FileOperator.logToFile("[Info|BSXQ] Collect power successfully.");
                }
            } else {
                FileOperator.logToFile("[Info|BSXQ] Collect no power.");
            }
        }
        return true;
    }

    private boolean checkForMainPage() {
        Rect rect = new Rect();
        rect.left = 10;
        rect.bottom = 1771 + Constant.Y_OFFSET;
        rect.right = 198;
        rect.top = 1633 + Constant.Y_OFFSET;
        String path = screenshotExecutor.takeElementShotByDefault(rect);
        if(path == null) {
            return false;
        }
        String result = ocrExecutor.contentRecognize(path);
        if(result.contains("星球")) {
            return true;
        }
        return false;
    }

    boolean checkCollectionSuccess(Rect rect){
        rect.left = 170;
        rect.bottom = 1320 + Constant.Y_OFFSET;
        rect.right = 860;
        rect.top = 670 + Constant.Y_OFFSET;
        String path = screenshotExecutor.takeElementShotByDefault(rect);
        if(path == null) {
            return false;
        }
        String result = ocrExecutor.contentRecognize(path);
        if(result.contains("成功")) {
            mDevice.click(469 + Constant.X_OFFSET, 1245 + Constant.Y_OFFSET);
            return true;
        } else {
            return false;
        }
    }

    public boolean chargePower() {
        int i = 3;
        while (--i > 0) {
            if(checkForMainPage()) {
                break;
            } else {
                mDevice.pressBack();
            }
        }
        if(i == 0){
            return false;
        }
        //click to main page
        mDevice.click(110 + Constant.X_OFFSET, 1700 + Constant.Y_OFFSET);
        //click to charge power
        mDevice.click(836 + Constant.X_OFFSET,1290 + Constant.Y_OFFSET);
         if(checkChargePowerPage()) {

         } else {
             return false;
         }

    }

    private boolean checkChargePowerPage() {
        Rect rect = new Rect();
        rect.left = 842;
        rect.bottom = 203 + Constant.Y_OFFSET;
        rect.right = 1062;
        rect.top = 82 + Constant.Y_OFFSET;
        String path = screenshotExecutor.takeElementShotByDefault(rect);
        if(path == null) {
            return false;
        }
        String result = ocrExecutor.contentRecognize(path);
        if(result.contains("能源")) {
            return true;
        } else {
            return false;
        }
    }

    public boolean enterBlueCenter() {
        int i = 3;
        while (--i > 0) {
            if(checkForMainPage()) {
                break;
            } else {
                mDevice.pressBack();
            }
        }
        if(i == 0){
            return false;
        }
        //click to main page
        mDevice.click(110 + Constant.X_OFFSET, 1700 + Constant.Y_OFFSET);
        //click to blue center
        mDevice.click(951 + Constant.X_OFFSET, 385 + Constant.Y_OFFSET);
        return true;
    }

}
