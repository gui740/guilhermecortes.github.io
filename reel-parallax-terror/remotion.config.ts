import {Config} from '@remotion/cli/config';
// tudo que está em assets/ vira staticFile('...')
Config.setPublicDir('assets');
Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(92);
Config.setConcurrency(4);
