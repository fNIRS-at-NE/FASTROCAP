import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Scanner;

import com.mbraintrain.smarting.streamer.device.SmartingDevice;
import com.mbraintrain.smarting.streamer.utils.ConnectUtil;
import com.retrocode.smarting.common.DeviceBuffer;
import com.retrocode.smarting.common.DeviceStatus;
import com.retrocode.smarting.common.command.DeviceChannel;
import com.retrocode.smarting.common.command.DeviceCommand;
import com.retrocode.smarting.common.command.DeviceCommandEnum;
import com.retrocode.smarting.common.callback.DeviceDataCallback;
import com.retrocode.smarting.common.callback.DeviceImpedanceCallback;

import edu.ucsd.sccn.LSL;

public class RunEEGandImp {

	@SuppressWarnings("unchecked")
	public static void main(String[] args) {

		ConnectUtil connectUtil = ConnectUtil.getInstance();

		System.out.println("Available ports:");
		List<String> portNames = connectUtil.getPortNames();
		portNames.forEach(portName -> {
			System.out.println(portNames.indexOf(portName) + ":" + portName);
		});

		//Scanner scanner = new Scanner(System.in);

		//String choice = scanner.nextLine();

		String chosen = "COM14"; // directly choose COM port

		System.out.println("Chosen port " + chosen);

		System.out.println("About to connect to a Smarting device...");
		connectUtil.connect(chosen);

		new Worker().start();

	}

	private static class Worker extends Thread implements DeviceImpedanceCallback, DeviceDataCallback{
		LSL.StreamOutlet streamOutlet = null;
		LSL.StreamOutlet streamOutletImp = null;
		List<DeviceChannel> selectedChannels = new ArrayList<>();

		@Override
		public void run() {

			SmartingDevice.instance().sendCommand(new DeviceCommand(DeviceCommandEnum.HZ250));
			SmartingDevice.instance().sendCommand(new DeviceCommand(DeviceCommandEnum.IMPON));
			SmartingDevice.instance().sendCommand(new DeviceCommand(DeviceCommandEnum.REFOFF));
			SmartingDevice.instance().sendCommand(new DeviceCommand(DeviceCommandEnum.NORMAL));

			Collections.addAll(selectedChannels, DeviceChannel.values());

			SmartingDevice.instance().setSelectedChannels(selectedChannels);
			SmartingDevice.instance().sendCommand(new DeviceCommand(DeviceCommandEnum.SELECT_CHANNELS, SmartingDevice.instance()));
			SmartingDevice.instance().sendCommand(new DeviceCommand(DeviceCommandEnum.ON));

			SmartingDevice.instance().addImpedanceCallback(this);
			System.out.println("Impedance streaming has started...");

			LSL.StreamInfo streamInfoImp = new LSL.StreamInfo("Impedances", "EEG", 30, 250, LSL.ChannelFormat.float32, "020287");

			try {
				streamOutletImp = new LSL.StreamOutlet(streamInfoImp);
			} catch (IOException e) {
				e.printStackTrace();
			}

			SmartingDevice.instance().addDataCallback(this);
			System.out.println("EEG data streaming has started...");

			LSL.StreamInfo streamInfo = new LSL.StreamInfo("EEG stream", "EEG", 24, 250, LSL.ChannelFormat.float32, "020287");

			try {
				streamOutlet = new LSL.StreamOutlet(streamInfo);
			} catch (IOException e) {
				e.printStackTrace();
			}

		}

		@Override
		public void onImpedance(double impedances[]) {

			DeviceStatus bufferbat = SmartingDevice.instance().queryStatus();
			byte sampleBat = 0;
			sampleBat = bufferbat.getBatteryLevel();
			double batlevel = sampleBat;

			DeviceBuffer buf_gyro = SmartingDevice.instance().getBuffer();
			// DeviceChannelBuffer sampleGyroX = 0;
			// sampleGyroX = buf_gyro_x.getGyroXbuffer();
			// double[] sampleGyro = new double[3];
			// sampleGyro[0] = buf_gyro_x.getGyroXbuffer().getAtCursor();


			DeviceBuffer buffer = SmartingDevice.instance().getBuffer();
			double[] sampleImp = new double[selectedChannels.size()+6];
			int cnt = 0;
			for (DeviceChannel ch : selectedChannels) {
				sampleImp[cnt++] = buffer.getBufferRaw(ch).getAtCursor();
			}

			sampleImp[26] = batlevel;
			sampleImp[27] = buf_gyro.getGyroXbuffer().getAtCursor();
			sampleImp[28] = buf_gyro.getGyroYbuffer().getAtCursor();
			sampleImp[29] = buf_gyro.getGyroZbuffer().getAtCursor();

			if (streamOutletImp != null) {
				streamOutletImp.push_chunk(sampleImp);
						}

		}

		@Override
		public void onData(String arg0) {

			DeviceBuffer buffer = SmartingDevice.instance().getBuffer();
			double[] sample = new double[selectedChannels.size()];
			int cnt = 0;
			for (DeviceChannel ch : selectedChannels) {
				sample[cnt++] = buffer.getBufferRaw(ch).getAtCursor();
			}
			if (streamOutlet != null) {
				streamOutlet.push_chunk(sample, buffer.getTimestampBuffer().getAtCursor());
			}

		}

	}
}
