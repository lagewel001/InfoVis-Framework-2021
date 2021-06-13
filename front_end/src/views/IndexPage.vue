from data import *;

<template>
  <div>
    <!-- Standard Mode -->
    <div v-if="!compare_mode" class="scale">
        <vs-row> <vs-col type="flex" vs-justify="left" vs-align="left" vs-lg="6" vs-sm="6" vs-xs="12">
                <transition mode="out-in" enter-active-class="animate__animated animate__fadeInLeft"
                            leave-active-class="animate__animated animate__fadeOutRight">
                    <vs-card class="cardx" v-if="fetched.img_existend">
                        <div slot="header">
                            <h3>Existing Art Pieces: {{ genre }}</h3>
                        </div>

                        <div slot="media">
                            <carousel-3d>
                                <slide v-for="(slide, i) in existend_imgs" :index="i" :key="i">
                                    <template slot-scope="{ index, isCurrent, leftIndex, rightIndex }">
                                        <img :data-index="index"
                                             :class="{ current: isCurrent, onLeft: (leftIndex >= 0), onRight: (rightIndex >= 0) }"
                                             :src="slide">
                                    </template>
                                </slide>
                            </carousel-3d>
                        </div>
                    </vs-card>
                </transition>
            </vs-col>

            <vs-col type="flex" vs-justify="right" vs-align="right" vs-lg="6" vs-sm="6" vs-xs="12" class="mt-sm-0 mt-4">
              <transition mode="out-in" enter-active-class="animate__animated animate__fadeInDown"
                          leave-active-class="animate__animated animate__fadeOutUp">
                <vs-card class="cardx" v-if="fetched.img_generated">
                  <div slot="header">
                      <h3>Generated Art Piece</h3>
                  </div>

                  <div slot="media">
                    <carousel-3d>
                      <slide v-for="(slide, i) in generated_imgs" :index="i" :key="i">
                        <template slot-scope="{ index, isCurrent, leftIndex, rightIndex }">
                          <img
                            :data-index="index"
                            :class="{ current: isCurrent, onLeft: (leftIndex >= 0), onRight: (rightIndex >= 0) }"
                            :src="slide">
                        </template>
                      </slide>
                    </carousel-3d>
                  </div>
                </vs-card>
              </transition>
            </vs-col>
        </vs-row>

        <vs-row :class="fetched.col_generated ? '' : 'mt-4'">
          <vs-col type="flex" vss-justify="left" vs-align="left" vs-lg="2" vs-sm="2" vs-xs="12">
            <vs-card class="cardx" v-if="donut_data[0].generated">
              <div slot="header"><h4>Colors in existing works</h4></div>
              <div slot="media">
                <pie-chart
                  :data="donut_data[0]"
                  :options="pie_options"
                  :key="donut_data[0].key">
                </pie-chart>
              </div>
            </vs-card>
          </vs-col>
          <vs-col type="flex" vss-justify="left" vs-align="left" vs-lg="2" vs-sm="2" vs-xs="12">
            <vs-card class="cardx" v-if="donut_data[1].generated">
              <div slot="header"><h4>Colors in generated works</h4></div>
              <div slot="media">
                <pie-chart
                  :data="donut_data[1]"
                  :options="pie_options"
                  :key="donut_data[1].key">
                </pie-chart>
              </div>
            </vs-card>
          </vs-col>
            <vs-col type="flex" vs-justify="left" vs-align="left" vs-lg="8" vs-sm="8" vs-xs="12">
                <transition mode="out-in" enter-active-class="animate__animated animate__fadeInRight"
                            leave-active-class="animate__animated animate__fadeOutLeft">
                    <vs-card class="cardx" v-if="fetched.summary">
                        <div slot="header"><h4>{{ genre }} on Wikipedia</h4></div>
                        <div style="font-size: 11pt">
                            {{ summary }}
                        </div>
                    </vs-card>
                </transition>
                <transition name="slide-fade">
                    <vs-card class="cardx" v-if="fetched.related_terms" height="100%">
                        <div slot="header"><h4>Related terms</h4></div>
                        <div>
                            {{ related_terms }}
                        </div>
                    </vs-card>
                </transition>
            </vs-col>
        </vs-row>

        <vs-row>
             <vs-col type="flex" vs-justify="left" vs-align="left" vs-lg="6" vs-sm="6" vs-xs="12">
                <transition mode="out-in" enter-active-class="animate__animated animate__fadeInUp"
                            leave-active-class="animate__animated animate__fadeOutDown">
                    <vs-card class="cardx" v-if="fetched.histograms">
                        <div slot="header"><h3>Distribution of dominant colors: {{ genre }}</h3></div>
                        <zingchart
                                ref="style_hist"
                                :data="style_hist_data"
                                :key="hist_key"
                        />
                    </vs-card>
                </transition>
            </vs-col>

            <vs-col type="flex" vs-justify="right" vs-align="right" vs-lg="6" vs-sm="6" vs-xs="12">
                <transition mode="out-in" enter-active-class="animate__animated animate__fadeInRight"
                            leave-active-class="animate__animated animate__fadeOutLeft">
                    <vs-card class="cardx" v-if="fetched.line_chart">
                        <div slot="header"><h3>Dominant colors over the years: {{ genre }}</h3></div>
                        <zingchart
                                ref="line_chart"
                                :data="line_chart_data"
                                :key="chart_key"
                                @node_mouseover="handleNodeHighlight"
                        />
                    </vs-card>
                </transition>
            </vs-col>
        </vs-row>
    </div>

    <!-- Compare Mode -->
    <div v-if="compare_mode" class="scale">
      <!-- -->
      <vs-row vs-justify="top">
        <vs-col type="flex" vs-justify="left" vs-align="left" vs-lg="6" vs-sm="6" vs-xs="12">
          <transition mode="out-in" enter-active-class="animate__animated animate__fadeInLeft"
                    leave-active-class="animate__animated animate__fadeOutRight">
            <vs-card class="cardx" style="border-style: solid; border-color:blue; border-width: thin;"
                     v-if="fetched.img_existend" fixedHeight vs-w="5">
                <div slot="header">
                    <h3>Existing Art Pieces: {{ genre }}</h3>
                </div>

                <div slot="media">
                    <carousel-3d>
                        <slide v-for="(slide, i) in existend_imgs" :index="i" :key="i">
                            <template slot-scope="{ index, isCurrent, leftIndex, rightIndex }">
                              <img :data-index="index"
                                   :class="{ current: isCurrent, onLeft: (leftIndex >= 0), onRight: (rightIndex >= 0) }"
                                   :src="slide">
                            </template>
                        </slide>
                    </carousel-3d>
                </div>
            </vs-card>
          </transition>
        </vs-col>

        <vs-col type="flex" vs-justify="right" vs-align="right" vs-lg="6" vs-sm="6" vs-xs="12" class="mt-sm-0 mt-4">
            <transition mode="out-in" enter-active-class="animate__animated animate__fadeInRight"
                        leave-active-class="animate__animated animate__fadeOutRight">
                <vs-card class="cardx" style="border-style: solid; border-color:orange; border-width: thin;"
                         v-if="fetched.img_existend" fixedHeight vs-w="5">
                    <div slot="header">
                        <h3>Existing Art Pieces: {{ exist_artist2 }}</h3>
                    </div>

                    <div slot="media">
                        <carousel-3d>
                            <slide v-for="(slide, i) in existend_imgs2" :index="i" :key="i">
                                <template slot-scope="{ index, isCurrent, leftIndex, rightIndex }">
                                    <img :data-index="index"
                                         :class="{ current: isCurrent, onLeft: (leftIndex >= 0), onRight: (rightIndex >= 0) }"
                                         :src="slide">
                                </template>
                            </slide>
                        </carousel-3d>
                    </div>
                </vs-card>
            </transition>
        </vs-col>
      </vs-row>

      <!-- -->
      <vs-row class="mt-4 mb-4">
          <vs-col type="flex" vs-justify="left" vs-align="left" vs-lg="6" vs-sm="6" vs-xs="12">
              <transition mode="out-in" enter-active-class="animate__animated animate__fadeInDown"
                          leave-active-class="animate__animated animate__fadeOutUp">
                  <vs-card class="cardx" style="border-style: solid; border-color:blue; border-width: thin;"
                           v-if="fetched.img_generated">
                    <div slot="header">
                      <h3>Generated Art Piece</h3>
                    </div>
                    <div slot="media">
                      <carousel-3d>
                        <slide v-for="(slide, i) in generated_imgs" :index="i" :key="i">
                          <template slot-scope="{ index, isCurrent, leftIndex, rightIndex }">
                            <img :data-index="index"
                                 :class="{ current: isCurrent, onLeft: (leftIndex >= 0), onRight: (rightIndex >= 0) }"
                                 :src="slide">
                          </template>
                        </slide>
                      </carousel-3d>
                    </div>
                  </vs-card>
              </transition>
          </vs-col>

          <vs-col type="flex" vs-justify="right" vs-align="right" vs-lg="6" vs-sm="6" vs-xs="12" class="mt-sm-0 mt-4">
              <transition mode="out-in" enter-active-class="animate__animated animate__fadeInDown"
                          leave-active-class="animate__animated animate__fadeOutUp">
                  <vs-card class="cardx" style="border-style: solid; border-color:orange; border-width: thin;"
                           v-if="fetched.img_generated">
                    <div slot="header">
                      <h3>Generated Art Piece</h3>
                    </div>
                    <div slot="media">
                      <carousel-3d>
                        <slide v-for="(slide, i) in generated_imgs2" :index="i" :key="i">
                          <template slot-scope="{ index, isCurrent, leftIndex, rightIndex }">
                            <img :data-index="index"
                                 :class="{ current: isCurrent, onLeft: (leftIndex >= 0), onRight: (rightIndex >= 0) }"
                                 :src="slide">
                          </template>
                        </slide>
                      </carousel-3d>
                    </div>
                  </vs-card>
              </transition>
          </vs-col>
      </vs-row>

      <!-- Wikipedia and piecharts -->
      <vs-row vs-justify='top'>
          <!-- Left artist -->
          <vs-col type="flex" vs-lg="6" vs-sm="6" vs-xs="12">
            <vs-row>
              <vs-col type="flex" vs-justify="flex-start" vs-lg="4" vs-sm="4" vs-xs="12" class="pl-0">
                <transition
                  mode="out-in"
                  enter-active-class="animate__animated animate__fadeInRight"
                  leave-active-class="animate__animated animate__fadeOutLeft">
                  <vs-card
                    class="cardx"
                    style="border-style: solid; border-color:blue; border-width: thin;"
                    v-if="donut_data[0].generated">
                    <div slot="header"><h4>Colors in existing works</h4></div>
                    <div slot="media">
                      <pie-chart
                        :data="donut_data[0]"
                        :options="pie_options"
                        :key="donut_data[0].key">
                      </pie-chart>
                    </div>
                  </vs-card>
                </transition>
                <transition
                  mode="out-in"
                  enter-active-class="animate__animated animate__fadeInRight"
                  leave-active-class="animate__animated animate__fadeOutLeft">
                  <vs-card
                    class="cardx"
                    style="border-style: solid; border-color:blue; border-width: thin;"
                    v-if="donut_data[1].generated">
                    <div slot="header"><h4>Colors in generated works</h4></div>
                    <div slot="media">
                      <pie-chart
                        :data="donut_data[1]"
                        :options="pie_options"
                        :key="donut_data[1].key">
                      </pie-chart>
                    </div>
                  </vs-card>
                </transition>
              </vs-col>
              <vs-col type="flex" vs-justify="flex-start" vs-lg="8" vs-sm="8" vs-xs="12" class="pl-0">
                <transition mode="out-in" enter-active-class="animate__animated animate__fadeInRight"
                            leave-active-class="animate__animated animate__fadeOutLeft">
                  <vs-card class="cardx"
                           style="border-style: solid; border-color:blue; border-width: thin;"
                           v-if="fetched.summary">
                    <div slot="header"><h4>{{ genre }} on Wikipedia</h4></div>
                    <div style="font-size: 11pt">
                        {{ summary }}
                    </div>
                  </vs-card>
                </transition>
                <transition name="slide-fade">
                  <vs-card class="cardx"
                           style="border-style: solid; border-color:blue; border-width: thin;"
                           v-if="fetched.related_terms">
                    <div slot="header"><h4>Related terms {{ genre }} </h4></div>
                    <div>
                      {{ related_terms }}
                    </div>
                  </vs-card>
                </transition>
              </vs-col>
            </vs-row>
          </vs-col>

          <!-- Right artist -->
          <vs-col type="flex" vs-lg="6" vs-sm="6" vs-xs="12">
            <vs-row>
              <vs-col type="flex" vs-justify="flex-start" vs-lg="4" vs-sm="4" vs-xs="12" class="pl-0">
                <transition
                  mode="out-in"
                  enter-active-class="animate__animated animate__fadeInRight"
                  leave-active-class="animate__animated animate__fadeOutLeft">
                  <vs-card
                    class="cardx"
                    style="border-style: solid; border-color:blue; border-width: thin;"
                    v-if="donut_data[2].generated">
                    <div slot="header"><h4>Colors in existing works</h4></div>
                    <div slot="media">
                      <pie-chart
                        :data="donut_data[2]"
                        :options="pie_options"
                        :key="donut_data[2].key">
                      </pie-chart>
                    </div>
                  </vs-card>
                </transition>
                <transition
                  mode="out-in"
                  enter-active-class="animate__animated animate__fadeInRight"
                  leave-active-class="animate__animated animate__fadeOutLeft">
                  <vs-card
                    class="cardx"
                    style="border-style: solid; border-color:blue; border-width: thin;"
                    v-if="donut_data[3].generated">
                    <div slot="header"><h4>Colors in generated works</h4></div>
                    <div slot="media">
                      <pie-chart
                        :data="donut_data[3]"
                        :options="pie_options"
                        :key="donut_data[3].key">
                      </pie-chart>
                    </div>
                  </vs-card>
                </transition>
              </vs-col>
              <vs-col type="flex" vs-justify="flex-start" vs-lg="8" vs-sm="8" vs-xs="12" class="pl-0">
                <transition mode="out-in" enter-active-class="animate__animated animate__fadeInRight"
                            leave-active-class="animate__animated animate__fadeOutLeft">
                  <vs-card class="cardx"
                           style="border-style: solid; border-color:blue; border-width: thin;"
                           v-if="fetched.summary">
                    <div slot="header"><h4>{{ genre2 }} on Wikipedia</h4></div>
                    <div style="font-size: 11pt">
                        {{ summary2 }}
                    </div>
                  </vs-card>
                </transition>
                <transition name="slide-fade">
                  <vs-card class="cardx"
                           style="border-style: solid; border-color:blue; border-width: thin;"
                           v-if="fetched.related_terms">
                    <div slot="header"><h4>Related terms {{ genre2 }} </h4></div>
                    <div>
                      {{ related_terms2 }}
                    </div>
                  </vs-card>
                </transition>
              </vs-col>
            </vs-row>
          </vs-col>
      </vs-row>

      <!-- Charts -->
      <vs-row vs-justify='top'>
          <vs-col type="flex" vs-justify="left" vs-align="left" vs-lg="6" vs-sm="6" vs-xs="12">
              <transition mode="out-in" enter-active-class="animate__animated animate__fadeInUp"
                          leave-active-class="animate__animated animate__fadeOutDown">
                  <vs-card class="cardx" v-if="fetched.histograms">
                      <div slot="header"><h3>Distribution of dominant Colors: {{ selected_artist }}</h3></div>
                      <zingchart ref="style_hist" :data="style_hist_data" :key="hist_key"></zingchart>
                  </vs-card>
              </transition>
          </vs-col>

          <vs-col type="flex" vs-justify="right" vs-align="right" vs-lg="6" vs-sm="6" vs-xs="12">
              <transition mode="out-in" enter-active-class="animate__animated animate__fadeInRight"
                          leave-active-class="animate__animated animate__fadeOutLeft">
                  <vs-card class="cardx" v-if="fetched.line_chart">
                      <div slot="header"><h3>Dominant Colors over the years: {{ selected_artist }}</h3></div>
                      <zingchart
                              ref="line_chart"
                              :data="line_chart_data"
                              :key="chart_key"
                              @node_mouseover="handleNodeHighlight"
                      />
                  </vs-card>
              </transition>
          </vs-col>
      </vs-row>
    </div>

    <!-- Timeline -->
    <vs-row>
        <vs-col type="flex" vs-justify="left" vs-align="left" id="timeline-card" :vs-w="12">
            <transition name="slide-fade">
                <vs-card class="cardx">
                    <div slot="header">
                        <h3>Make a<span v-if="fetched.img_generated"> new</span> selection!</h3>
                    </div>
                    <div class="col-12">
                        <div class="ml-4 mr-4">
                            <v-row>
                                <v-combobox class="col-md-4 col-5" v-model="pending_add_artists" :items="all_artists"
                                            label="Add artist(s) to timeline"
                                            hide-selected small-chips multiple>
                                    <template v-slot:prepend-inner>
                                        <v-progress-circular id="add-spinner" :size="20" :width="3"
                                                             style="display: none;" indeterminate color="primary">
                                        </v-progress-circular>
                                    </template>
                                    <template v-slot:append>
                                        <v-btn height="auto" @click="addArtists" text>Add</v-btn>
                                    </template>
                                </v-combobox>
                                <v-combobox class="col-md-4 offset-md-1 offset-2 col-5" v-model="pending_remove_artists"
                                            :items="artists_on_timeline"
                                            label="Remove artist(s)" hide-selected small-chips
                                            multiple>
                                    <template v-slot:prepend-inner>
                                        <v-progress-circular id="remove-spinner" :size="20" :width="3"
                                                             style="display: none;" indeterminate color="primary">
                                        </v-progress-circular>
                                    </template>
                                    <template v-slot:append>
                                        <v-btn height="auto" @click="removeArtists" text>Remove</v-btn>
                                    </template>
                                </v-combobox>

                                <div class="col-md-2 offset-md-1 col-12">
                                    <label class="container">Compare Mode
                                        <input type="checkbox" id="checkbox" v-model="compare_mode">
                                        <span class="checkmark"></span>
                                    </label>
                                </div>
                            </v-row>
                        </div>
                    </div>
                    <div class="mt-3" id="timeline">
                        Painting happy little trees...
                    </div>
                </vs-card>
            </transition>
        </vs-col>
    </vs-row>
  </div>
</template>

<script>
import * as d3 from "d3";
import PieChart from "./PieChart.js";
/*eslint no-unused-vars: 0*/
import zingchart from 'zingchart';
import zingchartVue from 'zingchart-vue';
import ResizeSensor from 'css-element-queries/src/ResizeSensor';
import TimelinesChart from "../timeline";
import 'animate.css';
import {Carousel3d, Slide} from 'vue-carousel-3d';

export default {
  name: 'Index',
  props: {
    main_color: {
        type: String,
    },
    logo: {
        type: String
    }
  },
  data: () => {
    return {
      compare_mode: false,
      compare: false,
      time_line_size: 12,
      // artist_options: [],
      // selected: 'airstream',
      genre: '',
      summary: '',
      related_terms: '',
      genre2: '',
      summary2: '',
      related_terms2: '',
      fetched: {
        img_existend: false,
        img_generated: false,
        col_generated: false,
        summary: false,
        related_terms: false,
        // artist_options: false,
        line_chart: false,
        histograms: false,
        img_existend2: false,
        img_generated2: false,
        col_generated2: false,
        summary2: false,
        related_terms2: false,
        line_chart2: false,
        histograms2: false,
      },
      generated_img: "@/assets/images/big/img1.jpg",
      existend_imgs: [],
      generated_imgs: [],
      generated_img2: "@/assets/images/big/img1.jpg",
      existend_imgs2: [],
      generated_imgs2: [],
      exist_title: '',
      exist_year: '',
      exist_artist: '',
      line_chart_data: {
        type: 'mixed',
        plot: {
          tooltip: {
            text: "%t\nHue: %v\nYear: %kt"
          },
          marker: {
              visible: true,
              style: ["#fff", "#aaa", "#000"],
          },
        },
        scaleX: {
            label: {
                "text": "Year",
            },
        },
        scaleY: {
            label: {
                "text": "Hue",
            },
            minValue: 0.0,
            maxValue: 1.0,
            step: 0.1,
        },
        series: [],
        legend: {
            // layout: "1x6", //row x column
            // x: "2%",
            // y: "68%",
        }
      },
      pie_options: {
        responsive: true,
        aspectRatio: 1,
        legend: { display: false },
      },
      donut_data: [
        {
          labels: [],
          datasets: [],
          key: 0,
        },
        {
          labels: [],
          datasets: [],
          key: 0,
        },
        {
          labels: [],
          datasets: [],
          key: 0,
        },
        {
          labels: [],
          datasets: [],
          key: 0,
        },
      ],
      pie_data: {
        labels: ["#e5856d", "#5e2812", "#e56b18", "#f6bab7", "#973f28"],
        datasets: [{
          backgroundColor: ["#e5856d", "#5e2812", "#e56b18", "#f6bab7", "#973f28"],
          data: [0.27, 0.14, 0.16, 0.22, 0.21],
        }]
      },
      pie_data2: {
        labels: ["#e5856d", "#5e2812", "#e56b18", "#f6bab7", "#973f28"],
        datasets: [{
          label: "Data One",
          backgroundColor: ["#e5856d", "#5e2812", "#e56b18", "#f6bab7", "#973f28"],
          data: [0.27, 0.14, 0.16, 0.22, 0.21]
        }]
      },
      style_hist_data: {
        type: 'hbar',
        plot: {
          aspect: "histogram",
          marker: {
              visible: false,
          },
          animation: {
              effect: 4,
              sequence: 1,
              speed: 10,
          },
        },
        plotarea: {
          "adjust-layout": true,
        },
        scaleX: {
          label: {
            "text": "Hue",
          },
          item: {
            offsetY: 0.05,
          },
          labels: [
            '0.0-0.1', '0.1-0.2', '0.2-0.3', '0.3-0.4', '0.4-0.5',
            '0.5-0.6', '0.6-0.7', '0.7-0.8', '0.8-0.9', '0.9-1.0',
          ],
        },
        scaleY: {
          // values: "0:1",
          label: {
            "text": "Density",
          },
        },
        series: [
          {values: [1, 2, 3, 4, 3, 4, 3, 2, 1]},
          {values: [5, 4, 3, 2, 1, 2, 3, 4, 5]},
          {values: [2, 3, 4, 3, 2, 3, 4, 2, 1]},
        ],
        legend: {},
        /*
        labels: [
          {
            // text: "Test",
            x: "0%",
            width: "100%",
            gradientColors: `
              #FF0000 #FF8000 #FFFF00 #80FF00
              #00FF00 #00FF80 #00FFFF #007FFF
              #0000FF #7F00FF #FF00FF #FF0080
              #FF0000
            `,
            gradientStops: ".001 .083 .167 .25 .333 .417 .5 .583 .667 .75 .833 .917 1",
            fillAngle: 0,
          }
        ],
        */
      },
      chart_key: 0,
      pie_key: 0,
      hist_key: 0,
      all_artists: [],
      selected_artist: "",
      pending_add_artists: [],
      timeline: TimelinesChart(),
      artists_on_timeline: [],
      pending_remove_artists: [],
      artPeriods: [
        {"name": "Medieval", "timeRange": [new Date(500, 1, 1), new Date(1400, 1, 1)]},
        {"name": "Renaissance", "timeRange": [new Date(1400, 1, 1), new Date(1500, 1, 1)]},
        {"name": "Mannerism", "timeRange": [new Date(1527, 1, 1), new Date(1580, 1, 1)]},
        {"name": "Baroque", "timeRange": [new Date(1600, 1, 1), new Date(1750, 1, 1)]},
        {"name": "Rococo", "timeRange": [new Date(1699, 1, 1), new Date(1780, 1, 1)]},
        {"name": "Neoclassicism", "timeRange": [new Date(1750, 1, 1), new Date(1850, 1, 1)]},
        {"name": "Romanticism", "timeRange": [new Date(1780, 1, 1), new Date(1850, 1, 1)]},
        {"name": "Realism", "timeRange": [new Date(1848, 1, 1), new Date(1900, 1, 1)]},
        {"name": "Art Nouveau", "timeRange": [new Date(1890, 1, 1), new Date(1910, 1, 1)]},
        {"name": "Impressionism", "timeRange": [new Date(1865, 1, 1), new Date(1885, 1, 1)]},
        {"name": "Post-impressionism", "timeRange": [new Date(1885, 1, 1), new Date(1910, 1, 1)]},
        {"name": "Fauvism", "timeRange": [new Date(1900, 1, 1), new Date(1935, 1, 1)]},
        {"name": "Expressionism", "timeRange": [new Date(1905, 1, 1), new Date(1920, 1, 1)]},
        {"name": "Cubism", "timeRange": [new Date(1907, 1, 1), new Date(1914, 1, 1)]},
        {"name": "Surrealism", "timeRange": [new Date(1917, 1, 1), new Date(1950, 1, 1)]},
        {"name": "Modern", "timeRange": [new Date(1950, 1, 1), new Date(2022, 1, 1)]},
      ]
    }
},
components: {
    PieChart,
    zingchart: zingchartVue,
    Carousel3d,
    Slide
    // 'overdrive': VOverdrive
},
methods: {
    handleNodeHighlight(e) {
        this.lastVisited = `Node: ${e.nodeindex} Value: ${e.value}`;
    },

    renderTimeline(data) {
        let container = document.getElementById('timeline');
        container.innerHTML = "";
        let filters = [];

        this.timeline
                .data(this.parseTimeLineData(data))
                .width(container.offsetWidth)
                .maxHeight(5000)
                .leftMargin(0)
                .rightMargin(0)
                .zQualitative(true)
                .timeFormat('%Y')
                .artPeriods(this.artPeriods)
                .showGroupTooltip(false)
                .showLineTooltip(false)
                .onZoom((a, b) => console.log(a, b))
                .onLegendClick((s) => {
                    this.setZoomToFilter();
                    window.setTimeout(() => {
                        let zoomStart = null, zoomEnd = null;

                        if (this.compare_mode) {
                            if (filters.includes(s.innerHTML)) {
                                // Deselect clicked filters
                                filters.splice(filters.indexOf(s.innerHTML));
                                if (filters.length === 0) {
                                    d3.selectAll('.series-segment')
                                            .attr('class', (d) => {
                                                return `series-segment ${d.val}`
                                            })
                                            .style('fill-opacity', .8);

                                    d3.selectAll('.color-slot').style('fill-opacity', 1);
                                    this.setZoomToFilter();
                                }
                            } else {
                                if (filters.length === 2) filters.shift();
                                filters.push(s.innerHTML);
                            }

                            if (filters.length == 2) {
                                this.time_line_size = 6;
                                this.$parent.socket.emit("get_artist_histograms", {
                                  artists: filters,
                                  type: "artist",
                                });
                                this.$parent.socket.emit("collect_scatter_data", {
                                    labels: filters,
                                    type: "artist",
                                });
                                this.selected_artist = filters;

                                // this.genre = filters[0];
                                // this.genre2 = filters[1]
                                this.$parent.socket.emit("collect_info", {
                                  type: "artists",
                                  compare_side: "left",
                                  class_idx: filters[0],
                                });
                                this.$parent.socket.emit("collect_info", {
                                  type: "artists",
                                  compare_side: "right",
                                  class_idx: filters[1],
                                });

                                this.$parent.socket.emit("generate_images", {
                                    type: "artists",
                                    compare_side: "left",
                                    amount: 7,
                                    class_idx: filters[0],
                                });
                                this.$parent.socket.emit("generate_images", {
                                    type: "artists",
                                    compare_side: "right",
                                    amount: 7,
                                    class_idx: filters[1],
                                });

                                // Select specific filters
                                d3.selectAll(`.series-segment.${filters.join(',.series-segment.')}`)
                                        .attr('class', (d) => {
                                            return `series-segment ${d.val}`
                                        })
                                        .style('fill-opacity', .8)
                                        .each((d, i) => {
                                            if (i === 0 && (!zoomStart || d.timeRange[0] < zoomStart)) zoomStart = d.timeRange[0]
                                            if (!zoomEnd || d.timeRange[1] > zoomEnd) zoomEnd = d.timeRange[1]
                                        });

                                d3.selectAll(`.color-slot.${filters.join(',color-slot.')}`)
                                        .style('fill-opacity', 1);

                                this.compare = true
                            }
                        }

                        if (!this.compare_mode) {
                            if (filters.includes(s.innerHTML)) {
                                // Deselect clicked filters
                                filters.splice(filters.indexOf(s.innerHTML));
                                if (filters.length === 0) {
                                    d3.selectAll('.series-segment')
                                            .attr('class', (d) => {
                                                return `series-segment ${d.val}`
                                            })
                                            .style('fill-opacity', .8);

                                    d3.selectAll('.color-slot').style('fill-opacity', 1);
                                    this.setZoomToFilter();
                                }
                            } else {
                                if (filters.length === 2) filters.shift();
                                filters.push(s.innerHTML);
                            }

                            if (filters.length > 0) {
                                this.time_line_size = 6;
                                this.$parent.socket.emit("get_artist_histograms", {
                                  artists: filters,
                                  type: "artist",
                                });
                                this.$parent.socket.emit("collect_scatter_data", {
                                    labels: filters,
                                    type: "artist",
                                });
                                this.selected_artist = filters;

                                this.genre = filters[filters.length - 1];
                                this.$parent.socket.emit("collect_info", {
                                    compare_side: "left",
                                    type: "artists",
                                    class_idx: filters[filters.length - 1],
                                });

                                this.$parent.socket.emit("generate_images", {
                                    compare_side: "left",
                                    type: "artists",
                                    amount: 7,
                                    class_idx: filters[filters.length - 1],
                                });

                                // Select specific filters
                                d3.selectAll(`.series-segment.${filters.join(',.series-segment.')}`)
                                        .attr('class', (d) => {
                                            return `series-segment ${d.val}`
                                        })
                                        .style('fill-opacity', .8)
                                        .each((d, i) => {
                                            if (i === 0 && (!zoomStart || d.timeRange[0] < zoomStart)) zoomStart = d.timeRange[0]
                                            if (!zoomEnd || d.timeRange[1] > zoomEnd) zoomEnd = d.timeRange[1]
                                        });

                                d3.selectAll(`.color-slot.${filters.join(',color-slot.')}`)
                                        .style('fill-opacity', 1);
                            }
                        }


                        // Deselect all not selected
                        d3.selectAll(`.series-segment:not(.${filters.join(',.')})`)
                                .attr('class', (d) => {
                                    return `series-segment ${d.val} disabled`
                                })
                                .style('fill-opacity', .1);

                        d3.selectAll(`.color-slot:not(.${filters.join(',.')})`)
                                .style('fill-opacity', .2);

                        this.setZoomToFilter(zoomStart, zoomEnd);
                    }, 1000);  // Hackerman to the rescue
                })
                .onArtPeriodTickClick((period) => {
                    console.log("Period selected", period);
                    this.setZoomToFilter(period.timeRange[0], period.timeRange[1]);
                    // TODO: Generate GAN based on selected art period

                    var start_year = period.timeRange[0].getFullYear();
                    var end_year = period.timeRange[1].getFullYear();
                    var avg_year = 0.5 * (start_year + end_year);
                    var century = Math.round(avg_year / 100);

                    var century2 = false

                    this.genre = century
                    this.genre2 = century


                    if (!this.compare_mode) {
                        this.$parent.socket.emit("get_artist_histograms", {
                          artists: [Math.round(avg_year)],
                          type: "centuries",
                        });
                        this.$parent.socket.emit("collect_scatter_data", {
                            labels: [Math.round(avg_year)],
                            type: "centuries",
                        });
                        this.$parent.socket.emit("collect_info", {
                            compare_side: "left",
                            type: "centuries",
                            class_idx: Math.round(avg_year),
                        });

                        this.$parent.socket.emit("generate_images", {
                            compare_side: "left",
                            type: "centuries",
                            amount: 7,
                            class_idx: century,
                        });
                    }
                    if (this.compare_mode) {
                        this.$parent.socket.emit("get_artist_histograms", {
                          artists: [Math.round(avg_year)],
                          type: "century",
                        });
                        this.$parent.socket.emit("collect_scatter_data", {
                            labels: [Math.round(avg_year)],
                            type: "century",
                        });
                        this.genre2 = century2
                        this.$parent.socket.emit("collect_info", {
                            compare_side: "left",
                            type: "centuries",
                            class_idx: Math.round(avg_year),
                        });
                        this.$parent.socket.emit("collect_info", {
                            compare_side: "right",
                            type: "centuries",
                            class_idx: century2,
                        });

                        this.$parent.socket.emit("generate_images", {
                            compare_side: "left",
                            type: "centuries",
                            amount: 7,
                            class_idx: century,
                        });

                        this.$parent.socket.emit("generate_images", {
                            compare_side: "right",
                            type: "centuries",
                            amount: 7,
                            class_idx: century2,
                        });
                    }
                })
                .onSegmentClick((s) => {
                    console.log("Painting selected", s);
                    // TODO: Generate GAN based on selected art piece


                    this.genre = s.val

                    if (!this.compare_mode) {
                        this.$parent.socket.emit("collect_info", {
                            compare_side: "left",
                            type: "artists",
                            class_idx: s.val,
                        });

                        this.$parent.socket.emit("generate_images", {
                            compare_side: "left",
                            type: "artists",
                            amount: 7,
                            class_idx: s.val,
                        });
                    }
                    if (this.compare_mode) {
                        this.genre2 = s.val2
                        this.$parent.socket.emit("collect_info", {
                            compare_side: "left",
                            type: "artists",
                            class_idx: s.val,
                        });
                        this.$parent.socket.emit("collect_info", {
                            compare_side: "right",
                            type: "artists",
                            class_idx: s.val2,
                        });

                        console.log("Generating artists images for comparison");
                        this.$parent.socket.emit("generate_images", {
                            compare_side: "left",
                            type: "artists",
                            amount: 7,
                            class_idx: s.val,
                        });
                        this.$parent.socket.emit("generate_images", {
                            compare_side: "right",
                            type: "artists",
                            amount: 7,
                            class_idx: s.val2,
                        });
                    }
                })(container);
    },
    setZoomToFilter(start = null, end = null) {
        this.timeline.zoomX(start && end ? [start, end] : [null, null]);
    },
    addArtists() {
        if (this.pending_add_artists.length > 0) {
            this.artists_on_timeline = this.artists_on_timeline.concat(this.pending_add_artists);
            console.log(this.artists_on_timeline);
            this.pending_add_artists = [];

            document.getElementById('add-spinner').style.display = "block";

            this.$parent.socket.emit('get_timeline_data', this.artists_on_timeline, true, (data) => {
                document.getElementById('add-spinner').style.display = "none";
                this.artists_on_timeline = data['artists'];
                this.renderTimeline(data['timelineData']);
            });
        }
    },
    removeArtists() {
        if (this.pending_remove_artists.some(e => this.artists_on_timeline.includes(e))) {
            this.artists_on_timeline = this.artists_on_timeline.filter(
                    e => !this.pending_remove_artists.includes(e)
            );
            this.pending_remove_artists = [];

            document.getElementById('remove-spinner').style.display = "block";

            this.$parent.socket.emit('get_timeline_data', this.artists_on_timeline, (data) => {
                document.getElementById('remove-spinner').style.display = "none";
                this.renderTimeline(data['timelineData']);
            });
        }
    },
    parseTimeLineData(data) {
        data.forEach(
                group => group.data.forEach(
                        label => label.data.forEach((painting) => {
                            painting.timeRange[0] = new Date(
                                    painting.timeRange[0]['year'],
                                    painting.timeRange[0]['month'],
                                    1
                            );
                            painting.timeRange[1] = new Date(
                                    painting.timeRange[1]['year'],
                                    painting.timeRange[1]['month'],
                                    1
                            );
                        })
                )
        );
        return data;
    },
    set_color_pie(index, colors, values) {
      this.donut_data[index].labels = colors;
      this.donut_data[index].datasets = [{
        data: values,
        backgroundColor: colors,
      }];
      this.donut_data[index].generated = true;
      this.donut_data[index].key += 1;
    }
},
async created() {
    this.$parent.socket.emit("get_all_artists", (all_artists) => this.all_artists = all_artists);
},
mounted: function () {
    this.$parent.socket.on("set_image", (data) => {
      window.scroll({top: 0, left: 0, behaviour: 'smooth'});

      if (data.compare_side == "left") {
        this.existend_imgs = data.existend_imgs;
        this.exist_title = data.title;
        this.exist_artist = data.artist;
        this.exist_year = data.year;
        this.fetched.img_existend = true;

        this.set_color_pie(0, data.colors.color_palette, data.colors.color_distribution);
      } else if (this.compare) {
        this.existend_imgs2 = data.existend_imgs;
        this.exist_title2 = data.title;
        this.exist_artist2 = data.artist;
        this.exist_year2 = data.year;
        this.fetched.img_existend2 = true;

        this.set_color_pie(2, data.colors.color_palette, data.colors.color_distribution);
      }
    });

    this.$parent.socket.on("get_style_hists", (data) => {
      this.style_hist_data.series = data.series;
      this.fetched.histograms = true;
      this.hist_key += 1;
    });

    this.$parent.socket.on("get_summary", (data) => {
      console.log("Received summary for ", data);
      if (data.compare_side == "left") {
        this.genre = data.genre;
        this.summary = data.summary;
        this.fetched.summary = true;
        this.related_terms = data.related_terms;
        this.fetched.related_terms = true;
      } else if (this.compare) {
        this.genre2 = data.genre;
        this.summary2 = data.summary;
        this.fetched.summary2 = true;
        this.related_terms2 = data.related_terms;
        this.fetched.related_terms2 = true;
      }
    });

    // this.$parent.socket.on("set_selected_artist", (data) => {
    //   this.artist_options = data.artist_options;
    //   this.fetched.artist_options = true;
    // });

    this.$parent.socket.on("collect_scatter_data", (data) => {
      this.line_chart_data.series = data.series;
      this.line_chart_data.plot.marker = data.plot.marker;
      this.fetched.line_chart = true;
      this.chart_key += 1;
      // if(this.compare) {
      //   this.line_chart_data.series = data.series;
      //   this.line_chart_data.plot.marker = data.plot.marker;
      //   console.log(this.line_chart_data);
      //   this.fetched.line_chart = true;
      //   this.chart_key += 1;
      // }
    });

    this.$parent.socket.on("images_generated", (data) => {
        console.log("Received generated image", data);
        if (data.success) {
          var images = [];
          data.images.forEach(image => {images.push(image.image)});
          var first = data.images[0];

          if (data.compare_side == "left") {
            this.generated_imgs = images;
            this.fetched.img_generated = true;

            this.set_color_pie(1, first.color_palette, first.color_distribution);
          } else if (this.compare) {
            this.generated_imgs2 = images;
            this.fetched.img_generated2 = true;

            this.set_color_pie(3, first.color_palette, first.color_distribution);
          }

          this.$parent.set_main_color(first.dominant_color);
        } else {
          this.generated_imgs = ["@/assets/images/big/img1.jpg"];

          if (this.compare) {
            this.generated_imgs2 = ["@/assets/images/big/img1.jpg"];
            this.fetched.img_generated2 = true;
          }
        }
        this.fetched.img_generated = true;
    });

    new ResizeSensor(document.getElementById('timeline-card'), () => {
        this.timeline.width(document.getElementById('timeline').clientWidth);
    });

    window.addEventListener("load", () => {
        this.$parent.socket.emit('get_timeline_data', (data) => {
            this.artists_on_timeline = data['artists'];
            this.renderTimeline(data['timelineData']);
        });
    });
  }
}
</script>

<style scoped>
  .slide-fade-enter-active {
      transition: all .9s ease;
  }

  .slide-fade-leave-active {
      transition: all .8s cubic-bezier(1.0, 0.5, 0.8, 1.0);
  }

  .slide-fade-enter, .slide-fade-leave-to {
      transform: translateX(10px);
      opacity: 0;
  }

  .scale {
      zoom: 1.0;
      -moz-transform: scale(1.0);
  }


  /* CHECKBOX

  /* Customize the label (the container) */
  .container {
      display: block;
      position: relative;
      padding-left: 40px;
      margin-bottom: 5px;
      cursor: pointer;
      font-size: 18px;
      color: rgb(93, 90, 90);
      -webkit-user-select: none;
      -moz-user-select: none;
      -ms-user-select: none;
      user-select: none;
  }

  /* Hide the browser's default checkbox */
  .container input {
      position: absolute;
      opacity: 0;
      cursor: pointer;
      height: 0;
      width: 0;
  }

  /* Create a custom checkbox */
  .checkmark {
      position: absolute;
      top: 10px;
      left: 0;
      height: 25px;
      width: 25px;
      background-color: #eee;
  }

  /* On mouse-over, add a grey background color */
  .container:hover input ~ .checkmark {
      background-color: #ccc;
  }

  /* When the checkbox is compare_mode, add a blue background */
  .container input:checked ~ .checkmark {
      background-color: #2196F3;
  }

  /* Create the checkmark/indicator (hidden when not compare_mode) */
  .checkmark:after {
      content: "";
      position: absolute;
      display: none;
  }

  /* Show the checkmark when compare_mode */
  .container input:checked ~ .checkmark:after {
      display: block;
  }

  /* Style the checkmark/indicator */
  .container .checkmark:after {
      left: 9px;
      top: 5px;
      width: 5px;
      height: 10px;
      border: solid white;
      border-width: 0 3px 3px 0;
      -webkit-transform: rotate(45deg);
      -ms-transform: rotate(45deg);
      transform: rotate(45deg);
  }
</style>
