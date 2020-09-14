package zhepan.com.mytestcase;

import android.support.test.InstrumentationRegistry;
import android.support.test.runner.AndroidJUnit4;
import android.support.test.uiautomator.UiDevice;

import org.junit.Test;
import org.junit.runner.RunWith;

import zhepan.com.mytestcase.baoshixingqiu.BSXQBasic;
import zhepan.com.mytestcase.common.FileOperator;

/**
 * Instrumented test, which will execute on an Android device.
 *
 * @see <a href="http://d.android.com/tools/testing">Testing documentation</a>
 */
@RunWith(AndroidJUnit4.class)
public class ExampleInstrumentedTest {
    private UiDevice mDevice;

    @Test
    public void useAppContext() throws Exception {
        mDevice = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation());
        mDevice.pressHome();
        mDevice.pressHome();
        FileOperator.logToFile("Start to test...");
        BSXQBasic bsxqBasic = new BSXQBasic(mDevice);
        if( bsxqBasic.collectPower()) {
            FileOperator.logToFile("[Success|BSXQ] is login.");
        } else {
            FileOperator.logToFile("[Failed|BSXQ] is not login.");
            throw new Exception("Exit");
        }

        if(!bsxqBasic.enterBlueCenter()) {
            throw new Exception("Exit");
        }

        FileOperator.logToFile("Finished the test.");

    }

}
