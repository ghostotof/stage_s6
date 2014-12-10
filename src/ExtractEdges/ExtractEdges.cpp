/*
 * ExtractEdges.cpp
 *
 *  Created on: 12 mai 2014
 *      Author: christophe
 */
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"
#include "opencv/cv.h"
#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include <string>

using namespace cv;
using namespace std;

/// Global variables

Mat src, src_gray;
Mat dst, detected_edges;

int edgeThresh = 1;
int lowThreshold;
int const max_lowThreshold = 100;
int ratio = 3;
int kernel_size = 3;

string pathSrc;
string pathDst;
string file;

CvHaarClassifierCascade *cascade;
CvMemStorage *storage;

/**
 * @function CannyThreshold
 * @brief Trackbar callback - Canny thresholds input with a ratio 1:3
 */
void CannyThreshold(int, void*) {
	/// Reduce noise with a kernel 3x3
	blur( src_gray, detected_edges, Size(3,3) );

	/// Canny detector
	Canny( detected_edges, detected_edges, lowThreshold, lowThreshold*ratio, kernel_size );

	/// Using Canny's output as a mask, we display our result
	dst = Scalar::all(0);

	src.copyTo( dst, detected_edges);

	// Face detection
	int i;
	IplImage image = src.operator IplImage();
	IplImage edges = dst.operator IplImage();

	// Recherche du visage sur la photo original
	CvSeq *faces = cvHaarDetectObjects(
	           &image,
	           cascade,
	           storage,
	           1.1,
	           3,
	           0 ,
	           cvSize( 40, 40 ) );

	// Sélection des contours du premier visage
	CvRect *r = ( CvRect* )cvGetSeqElem( faces, 0 );
	IplImage *dest = cvCreateImage(cvSize(r->width, r->height), image.depth, image.nChannels);

	cvSetImageROI(&edges, *r);
	cvCopyImage(&edges, dest);

	IplImage *dest_fin = cvCreateImage(cvSize(40, 40), dest->depth, dest->nChannels);
	cvResize(dest, dest_fin);
	Mat gray_image;
	cvtColor(Mat(dest_fin), gray_image, CV_BGR2GRAY);

	imwrite(pathDst + file, gray_image);

	cvResetImageROI(&edges);
	cvReleaseImage(&dest);
	cvReleaseImage(&dest_fin);
}


/** @function main */
int main( int argc, char** argv )
{
	if ( argc <= 4) {
		cout << "Problème nombre d'arguments" << endl;
		cout << "Usage : ExtractEdges [pathSrc] [pathDst] [fileName] [threshold]" << endl;
		return -1;
	}

	pathSrc = argv[1];
	pathDst = argv[2];
	file = argv[3];
	lowThreshold = atoi(argv[4]);

	cascade = (CvHaarClassifierCascade*) cvLoad("haarcascade_frontalface_alt.xml", 0, 0, 0);
	storage = cvCreateMemStorage(0);

	// cout << pathSrc + file << endl;

	/// Load an image
	src = imread( pathSrc + file );

	if( !src.data ) {
		cout << "Problème d'ouverture : " + pathSrc + file << endl;
		cvReleaseHaarClassifierCascade(&cascade);
		cvReleaseMemStorage(&storage);
		return -1;
	}

	/// Create a matrix of the same type and size as src (for dst)
	dst.create( src.size(), src.type() );

	/// Convert the image to grayscale
	cvtColor( src, src_gray, CV_BGR2GRAY );

	/// Show the image
	CannyThreshold(0, 0);

	cvReleaseHaarClassifierCascade(&cascade);
	cvReleaseMemStorage(&storage);

	return 0;
}
