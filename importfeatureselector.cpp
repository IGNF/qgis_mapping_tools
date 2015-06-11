#include "importfeatureselector2.h"
#include "ui_importfeatureselector2.h"

importFeatureSelector2::importFeatureSelector2(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::importFeatureSelector2)
{
    ui->setupUi(this);
}

importFeatureSelector2::~importFeatureSelector2()
{
    delete ui;
}
